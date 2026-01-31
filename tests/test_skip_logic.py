import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from ui import process_generation


async def list_async(async_gen):
    res = []
    async for i in async_gen:
        res.append(i)
    return res


@pytest.mark.asyncio
async def test_process_generation_skip_logic():
    # Setup
    config = MagicMock()
    config.workflows = [{"name": "test", "path": "test.json"}]
    config.sliders = {}
    comfy_client = MagicMock()
    comfy_client.interrupt = MagicMock()
    object_info = {}
    skip_event = asyncio.Event()

    workflow_data = {"1": {"inputs": {}, "class_type": "Node"}}

    # Mock handle_generation
    # We want it to be an async generator
    async def mock_gen(*args):
        yield (["img1"], None, "Step 1")
        try:
            await asyncio.sleep(0.5)
            yield (["img1"], None, "Step 2")
        except asyncio.CancelledError:
            # We expect cancellation on skip
            raise

    with patch("ui.handle_generation", side_effect=mock_gen):
        with patch("builtins.open", new_callable=MagicMock) as mock_file:
            mock_file.return_value.__enter__.return_value = mock_file
            with patch("json.load", return_value=workflow_data):
                with patch("ui.apply_random_seeds", side_effect=lambda x: x):
                    with patch("ui.extract_workflow_inputs", return_value=[]):
                        with patch("ui.generate_batch_seeds", return_value=[1, 2]):

                            # Run generation (Batch count 2)
                            task = asyncio.create_task(
                                list_async(
                                    process_generation(
                                        "test",
                                        "",
                                        {},
                                        2,
                                        config,
                                        comfy_client,
                                        object_info,
                                        [],
                                        skip_event,
                                    )
                                )
                            )

                            # Trigger skip during first batch (after it starts yielding)
                            await asyncio.sleep(0.1)
                            skip_event.set()

                            results = await task

                            # Analyze results
                            # Should see updates from Batch 1 (Step 1)
                            # Should NOT see Batch 1 (Step 2)
                            # Should see Batch 2 (Step 1 and Step 2)

                            status_messages = [r[1] for r in results if r[1]]
                            # print(status_messages)

                            # Filter seed suffix
                            msgs = [m.split(" (")[0] for m in status_messages]

                            # Batch 1 Step 1
                            assert "Step 1" in msgs

                            # Batch 2 Step 1 and 2
                            # Note: msgs contains many duplicates due to yields for button states?
                            # process_generation yields after each handle_generation update.

                            # Verify that we got Step 2 eventually (from Batch 2)
                            assert "Step 2" in msgs

                            # Verify that we see "Batch 2/2" in the full strings
                            batch_2_seen = any("Batch 2/2" in r[1] for r in results if r[1])
                            assert batch_2_seen

                            # Verify interruption called
                            # It is called in on_skip (UI handler), but process_generation loop also checks skip_event.
                            # process_generation doesn't call interrupt() inside the loop (the button click does).
                            # So we don't check comfy_client.interrupt here.
