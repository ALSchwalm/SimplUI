# Specification: Compact Connection Status Indicator with Custom Tooltip

## Overview
This track simplifies the connection status indicator in the header. Instead of a large badge showing the full connection text (which takes up too much layout space, particularly on mobile), the status indicator will always be rendered as a compact status dot (green for connected, red for disconnected). When hovered, a custom CSS-styled tooltip will display the status details.

## Functional Requirements
1. **Compact Indicator Layout:**
   - Update the `.connection-status` layout to only show the status dot.
   - The text label (`.status-text`) must be hidden from view.
   - The indicator container should have a round or small pill shape (e.g. just wrapping the dot, padding adjusted).
2. **Dynamic Tooltip Information:**
   - The connection status details must be stored in a `data-tooltip` attribute on the `#connection-status` element.
   - When the connection state updates in JS, the `data-tooltip` attribute must be updated with the description (e.g., 'ComfyUI Server Online' or 'ComfyUI Server Offline').
3. **Custom CSS Tooltip:**
   - Implement a hover-triggered tooltip using CSS pseudo-elements (`::after`) on `#connection-status`.
   - The tooltip must feature premium styling: dark glassmorphism background, subtle border, smooth fade-in/fade-out transitions, and correct alignment (positioned underneath the indicator).

## Acceptance Criteria
- The connection status in the header is a compact dot without visible label text.
- Hovering over the connection dot reveals a custom styled tooltip with the status details.
- When connected, the dot is green with a subtle green glow.
- When disconnected, the dot is red with a subtle red glow.
- Tooltip successfully displays "ComfyUI Server Online" or "ComfyUI Server Offline" based on actual connection state.
