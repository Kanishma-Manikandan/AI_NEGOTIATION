class YourBuyerAgent(BaseBuyerAgent):
    """
    YOUR BUYER AGENT IMPLEMENTATION
    
    Tips for success:
    1. Stay in character - consistency matters!
    2. Never exceed your budget
    3. Aim for the best deal, but know when to close
    4. Use market price as reference
    5. Maximum 10 rounds - don't let negotiations timeout
    """
    
    def define_personality(self) -> Dict[str, Any]:
        """
        Define your agent's unique personality
        """
        return {
            "personality_type": "diplomatic",
            "traits": ["patient", "persuasive", "friendly"],
            "negotiation_style": "I aim for a win-win situation, focusing on building rapport while negotiating.",
            "catchphrases": ["Let's find a middle ground.", "I appreciate your offer, but..."]
        }
    
    def generate_opening_offer(self, context: NegotiationContext) -> Tuple[int, str]:
        """
        Generate your opening offer
        """
        # Start with a reasonable offer based on market price
        opening_price = int(context.product.base_market_price * 0.75)  # 25% below market
        opening_price = min(opening_price, context.your_budget)
        
        message = f"I'd like to offer ₹{opening_price} for the {context.product.name}. I believe this is a fair starting point."
        
        return opening_price, message
    
    def respond_to_seller_offer(self, context: NegotiationContext, seller_price: int, seller_message: str) -> Tuple[DealStatus, int, str]:
        """
        Implement your response strategy
        """
        # Accept if the seller's price is within budget and reasonable
        if seller_price <= context.your_budget and seller_price <= context.product.base_market_price * 0.85:
            return DealStatus.ACCEPTED, seller_price, f"Thank you for your offer! I accept the deal at ₹{seller_price}."
        
        # Counter-offer logic
        if context.current_round >= 8:  # Close to timeout
            counter_offer = min(int(seller_price * 0.95), context.your_budget)
        else:
            counter_offer = min(int(seller_price * 0.90), context.your_budget)
        
        message = f"I appreciate your offer, but I can only go up to ₹{counter_offer}."
        
        return DealStatus.ONGOING, counter_offer, message
    
    def get_personality_prompt(self) -> str:
        """
        Write a detailed prompt for your agent's communication style
        """
        return """
        I am a diplomatic buyer who values collaboration and mutual benefit. I communicate in a friendly and respectful manner, often using phrases like 'Let's find a middle ground' to encourage dialogue. My approach is patient, and I aim to build rapport while negotiating, ensuring that both parties feel satisfied with the outcome.
        """

    # ============================================
    # OPTIONAL: Add helper methods below
    # ============================================
    
    def analyze_negotiation_progress(self, context: NegotiationContext) -> Dict[str, Any]:
        """Optional: Analyze how the negotiation is progressing"""
        # This could be used to adjust strategies based on rounds or offers
        pass
    
    def calculate_fair_price(self, product: Product) -> int:
        """Optional: Calculate what you consider a fair price"""
        # This could be based on quality grade and market trends
        return int(product.base_market_price * 0.85)  # Example logic
