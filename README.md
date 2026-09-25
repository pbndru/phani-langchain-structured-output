# Provider Strategy

Some model providers support structured output natively through their APIs (e.g. OpenAI, xAI (Grok), Gemini, Anthropic (Claude)). This is the most reliable method when available.
To use this strategy, configure a ProviderStrategy

# Run -> uv run .\provider-strategy.py 
# Output: name='John Doe' email='john@example.com' phone='(555) 123-4567'


# Tool calling strategy

For models that don’t support native structured output, LangChain uses tool calling to achieve the same result. This works with all models that support tool calling (most modern models).

# Run -> uv run .\tool-calling-strategy.py 
# Output: rating=5 sentiment='positive' key_points=['great product', 'fast shipping', 'expensive']

# Custom tool message content

The tool_message_content parameter allows you to customize the message that appears in the conversation history 
when structured output is generated:

# Run -> uv run .\custom-tool-message-content.py 
# Output: Action item captured and added to meeting notes!

# Multiple structured outputs error
When a model incorrectly calls multiple structured output tools, the agent provides error feedback in a ToolMessage and prompts the model to retry:
# Run -> uv run .\multiple-structured-outputs-error.py 
# Output: 
--- Structured Outcome ---
name='John Doe' email='john@email.com'

# Execution environment
Agents are especially useful when they can take action rather than just generate text. The execution environment gives the agent a workspace: tools it can call, a filesystem for reading and writing files across turns, and code execution for running scripts or shell commands.
# Run -> uv run .\execution-envrionment.py 
# Output: 
Sending query to agent: 'Search the local data for quarterly financial reports and summarize them.'...

=== Agent Final Output ===
I searched the local data for "quarterly financial reports," but the search result did not return any accessible files or content that I can read and summarize.

Could you please provide:
1. **The directory path** where these reports are located?
2. **Specific file names** (e.g., `Q3_2024_Report.pdf`)?
3. Any other details about the format or location of the data?

Once I have access to the documents, I will be happy to summarize them for you.

# Context Management
Every model call has a fixed context window. As an agent runs, that window fills with accumulating history, tool results, and intermediate steps. Summarization compresses history before overflow hits; memory loads persistent instructions at startup so knowledge carries across sessions; skills surface domain knowledge on demand rather than loading everything upfront.
# Run -> uv run .\context-management.py 
# Output: 
==================================================
Executing Practice Test Input: 'Can you help me brew a great IPA? Show me the recipe layout.'
==================================================

[SYSTEM ACTION] Tool activated! Searching archive for: 'IPA brewing recipe'

================ FINAL AGENT OUTPUT ================
That sounds like a fun project! Brewing an IPA (India Pale Ale) is very rewarding. The "recipe layout" isn't one single thing, but rather a structured plan covering ingredients, process steps, and target measurements.

Based on common professional brewing standards, here is a comprehensive recipe layout you can use as a template. You can fill in the specifics for your desired batch size and flavor profile!

***

### 🍺 IPA Recipe Layout Template

#### **I. General Information & Goals**
*   **Recipe Name:** (e.g., Tropical Sunset IPA)
*   **Target Batch Size:** (e.g., 20 Litres / 5 Gallons)
*   **Target ABV (Alcohol by Volume):** (e.g., 6.8% - 7.5%)
*   **Target IBU (International Bitterness Units):** (How bitter it is, typically 40-70 for a modern IPA)
*   **Target SRM/Color:** (The color of the beer; e.g., 6-10 SRM / Amber to Gold)

#### **II. Grain Bill (Malts)**
This section dictates the body, color, and foundational sweetness of the beer. The total weight should equal your target batch size's grain requirement.

| Malt Type | Purpose | Weight (kg/lbs) | Notes |
| :--- | :--- | :--- | :--- |
| **Base Malt** (e.g., Maris Otter, Pale Ale Malt) | Provides the bulk of the fermentable sugars and foundation flavor. | [Weight] | This is your primary ingredient. |
| **Crystal/Caramel Malts** (e.g., Crystal 40L, Munich) | Adds color, body, and residual sweetness/complexity. | [Weight] | Use sparingly to avoid making the beer too sweet. |
| **Specialty Malt** (Optional) | For unique flavor notes (e.g., Wheat, Chocolate). | [Weight] | Only if needed for a specific style variation. |

#### **III. Hop Schedule**
Hops provide bitterness (IBU), aroma, and flavor. They are added at different stages of the boil for different effects.

| Hops Variety | Type/Goal | Weight (g/oz) | Timing in Boil | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **Bittering Hops** (e.g., Magnum, Warrior) | Bitterness (IBU). | [Weight] | 60 Minutes | To establish the core bitterness and balance malt sweetness. |
| **Flavor Hops** (e.g., Cascade, Centennial) | Mid-boil flavor notes. | [Weight] | 20 - 45 Minutes | Adds complexity and aromatic backbone. |
| **Aroma/Dry Hop Hops** (e.g., Citra, Mosaic, Galaxy) | Intense aroma at the end. | [Weight] | 0 Minutes (After Fermentation) | The "IPA punch." These are added late to preserve delicate oils. |

#### **IV. Yeast & Water Profile**
*   **Yeast Strain:** (e.g., US-05, Wyeast 1084 Irish Ale, specific IPA strain)
    *   *Goal:* Select a yeast that complements the hop profile and achieves your desired attenuation (how dry or sweet the beer finishes).
*   **Water Profile Adjustments (Optional):** If you are using local water, you might need to adjust mineral content (e.g., adding gypsum for sulfates if needed) to optimize flavor.

#### **V. Brewing Process Steps (The Boil)**
1.  **Mash:** Mix the grains and steep/mash them according to your grain bill's instructions to convert starches into fermentable sugars.
2.  **Lauter/Sparge:** Separate the liquid (wort) from the spent grains.
3.  **Boil:** Bring the wort to a rolling boil for **60 minutes**. Add hops and ingredients at specified times.
4.  **Chill:** Rapidly cool the wort down to pitching temperature (usually 18-22°C / 65-72°F).
5.  **Pitch Yeast:** Transfer the cooled, sweet wort into your sanitized fermenter and add the yeast slurry/liquid.
6.  **Fermentation:** Let the beer ferment at the recommended temperature for the yeast strain until gravity readings stabilize (this can take days or weeks).
7.  **Dry Hopping & Conditioning:** Once fermentation is complete, add the dry hops (Aroma Hops) and let the beer sit ("condition") to allow the hop aromas to fully integrate.
8.  **Packaging:** Bottle or keg the finished product!

***

### 💡 Pro-Tip for a Great IPA:

The key to modern IPAs is often **Hop Variety**. Don't just use one type of hop; try pairing hops from different families (e.g., combining citrus notes like Citra with tropical notes like Mango or passionfruit).

Let me know what kind of flavor profile you are aiming for (Citrusy, Piney, Tropical, Earthy), and I can help you refine this layout!
====================================================