from prompts.real_estate import REAL_ESTATE_PROMPT
from prompts.car_rental import CAR_RENTAL_PROMPT
from prompts.demo import DEMO_SALES_PROMPT

# Registry maps niche key (stored in AgentConfig.niche) to the system prompt string.
# Adding a new vertical = add one line here. No changes to agent.py required.
PROMPT_REGISTRY: dict = {
    "real_estate": REAL_ESTATE_PROMPT,
    "car_rental": CAR_RENTAL_PROMPT,
    "demo": DEMO_SALES_PROMPT,
    "sales_demo": DEMO_SALES_PROMPT,
}
