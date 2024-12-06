import streamlit as st

from style_helper import apply_header, card_container

def main():    
    apply_header()
    st.title("Understanding Dementia")

    st.markdown(
      """
      <div class="button-grid">
          <a href="exercise_routines" target="_self" class="button-card">
            <p>View Routines</p>
            <div class="icon">&#129488;</div>
          </a>
          <a href="exercise_log" target="_self" class="button-card">
            <p>Exercise Log</p>
            <div class="icon">&#128200;</div>
          </a>
      </div>
      """, unsafe_allow_html=True)

    st.sidebar.image("https://raw.githubusercontent.com/datjandra/kupuna/refs/heads/main/images/logo.png")
    
    # Sidebar with links
    st.sidebar.header("Helpful Links")
    st.sidebar.markdown("""
    - [Hawaiʻi Alzheimer’s Disease Initiative](https://manoa.hawaii.edu/aging/hadi/)
    - [Alzheimer's Association](https://www.alz.org/)
    - [Alzheimer's Disease International](https://www.alzint.org/)
    """)

    st.markdown("""
    ### What is Dementia?
    Dementia is not a specific disease but a general term for a decline in mental ability severe enough to interfere with daily life. Memory loss is a common symptom.

    In Hawaiʻi, where `ohana` (family) is central, caring for loved ones with dementia often involves the whole family. Understanding this condition can help families provide better support and care.
    
    ---
    
    ### Common Signs of Dementia:
    - Forgetting names, dates, or recent events
    - Difficulty with problem-solving or planning
    - Getting lost in familiar places
    - Trouble with communication, like finding the right words
    - Changes in mood or personality, such as confusion or withdrawal

    ---

    ### Causes of Dementia:
    The most common cause of dementia is Alzheimer's disease, which accounts for 60-80% of cases. Other causes include:
    - **Vascular dementia**: Caused by reduced blood flow to the brain.
    - **Lewy body dementia**: Associated with abnormal protein deposits in the brain.
    - **Frontotemporal dementia**: Affects the brain areas related to behavior and language.

    Dementia affects people worldwide, regardless of culture, but family and community play key roles in caregiving, just like in Hawaiʻi’s `ohana`.

    ---

    ## Caring for Someone with Dementia:
    Caring for someone with dementia can be challenging, but there are ways to make life easier for everyone involved:
    1. **Be Patient**: Memory loss can be frustrating for your loved one.
    2. **Create a Routine**: Familiar schedules help reduce confusion.
    3. **Stay Active**: Gentle activities like walking, tai chi, or even dance can improve mood and mobility.
    4. **Adapt the Environment**: Remove tripping hazards and use clear labels for items.
    5. **Ask for Help**: Seek support groups, home care services, or online communities.
    
    ### Aloha Spirit in Care:
    The `aloha spirit` (kindness, love, and compassion) found in Hawaiʻi offers a valuable reminder to approach caregiving with patience and empathy. Whether in Hawaiʻi or elsewhere, a loving approach can make a big difference.
    
    ---

    ## Tips to Reduce Risk of Dementia:
    While there is no guaranteed way to prevent dementia, you can lower your risk with these steps:
    - **Stay Physically Active**: Exercise regularly, even simple walks or yoga.
    - **Eat a Balanced Diet**: Include fruits, vegetables, whole grains, and healthy fats.
    - **Keep Your Brain Engaged**: Try puzzles, read, or learn something new.
    - **Stay Connected**: Social activities and strong relationships benefit brain health.
    - **Manage Health Conditions**: Control high blood pressure, diabetes, and other conditions that can affect brain function.
    
    ---

    ## Global Perspective on Dementia:
    Dementia affects over **55 million people worldwide**, and the number is expected to grow as populations age. Caregivers often face similar challenges across cultures, such as balancing work and caregiving or finding adequate support systems.
    
    In the U.S., organizations like the Alzheimer's Association provide valuable resources. Globally, groups like the World Health Organization (WHO) and Alzheimer's Disease International offer support for caregivers and advocate for dementia research and awareness.
    
    ---

    ### Conclusion
    Dementia is a challenging condition, but with the aloha spirit and support from your `ohana`, you can create a loving and supportive environment for those affected. Remember to take care of yourself too—caring for a loved one is a journey best shared with others.
    """)

if __name__ == "__main__":
    main()
