# Product Guidelines

## Visual Identity
- **Minimalist and Clean:** The user interface should prioritize clarity and ease of use. This means minimizing visual clutter, using whitespace effectively, and ensuring that the most important actions are the most prominent.
- **Gradio Focused:** Leverage Gradio's built-in components and layout options to maintain a consistent and standard web UI feel while keeping customization focused on usability.

## Interaction Design
- **Integrated Sidebar:** The "Advanced" sidebar should use an integrated approach where it slides in smoothly, adjusting the main content to make room. This transition should feel cohesive with the rest of the application.
- **Feedback Loops:** Provide clear, professional feedback during long-running tasks like image generation (e.g., progress bars, loading indicators).
- **Viewport Optimization:** Ensure that large visual assets, such as generated images and live previews, do not overwhelm the UI. Use responsive height constraints (e.g., 50vh) and 'contain' scaling to keep images within the viewport.
- **Simplified Dimensions:** Prioritize user-friendly dimension controls (Aspect Ratio and Pixel Count) over raw pixel inputs. Ensure all calculated dimensions are optimized for generative models (e.g., multiples of 64).
- **Responsive Gallery:** Image galleries (main results and history) should adapt their column count to the screen size, switching between 1 column for mobile view and 2 columns for desktop view.
- **Layout Constraints:** Maintain a maximum application width of 1280px on large displays to preserve readability and usability, centering the content horizontally.

## Voice and Tone
- **Professional and Helpful:** Use clear, direct, and helpful language for all labels, tooltips, and instructions.
- **Accessible Complexity:** When presenting advanced controls, use descriptive labels that help explain what the control does, reducing the learning curve for users who are just starting to explore advanced features.
