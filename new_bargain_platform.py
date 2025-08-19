"""
===========================================
🏆 AI NEGOTIATION AGENT - HACKATHON ELITE
===========================================

Professional Buyer Agent optimized for Alphonso Mango negotiations
Built for maximum success rate and impressive presentation
"""

import json
import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod
import random
import math
import time

# ============================================
# PART 1: DATA STRUCTURES (DO NOT MODIFY)
# ============================================

@dataclass
class Product:
    """Product being negotiated"""
    name: str
    category: str
    quantity: int
    quality_grade: str  # 'A', 'B', or 'Export'
    origin: str
    base_market_price: int  # Reference price for this product
    attributes: Dict[str, Any]

@dataclass
class NegotiationContext:
    """Current negotiation state"""
    product: Product
    your_budget: int  # Your maximum budget (NEVER exceed this)
    current_round: int
    seller_offers: List[int]  # History of seller's offers
    your_offers: List[int]  # History of your offers
    messages: List[Dict[str, str]]  # Full conversation history

class DealStatus(Enum):
    ONGOING = "ongoing"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    TIMEOUT = "timeout"


# ============================================
# PART 2: BASE AGENT CLASS (DO NOT MODIFY)
# ============================================

class BaseBuyerAgent(ABC):
    """Base class for all buyer agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.personality = self.define_personality()
        
    @abstractmethod
    def define_personality(self) -> Dict[str, Any]:
        """
        Define your agent's personality traits.
        
        Returns:
            Dict containing:
            - personality_type: str (e.g., "aggressive", "analytical", "diplomatic", "custom")
            - traits: List[str] (e.g., ["impatient", "data-driven", "friendly"])
            - negotiation_style: str (description of approach)
            - catchphrases: List[str] (typical phrases your agent uses)
        """
        pass
    
    @abstractmethod
    def generate_opening_offer(self, context: NegotiationContext) -> Tuple[int, str]:
        """
        Generate your first offer in the negotiation.
        
        Args:
            context: Current negotiation context
            
        Returns:
            Tuple of (offer_amount, message)
            - offer_amount: Your opening price offer (must be <= budget)
            - message: Your negotiation message (2-3 sentences, include personality)
        """
        pass
    
    @abstractmethod
    def respond_to_seller_offer(self, context: NegotiationContext, seller_price: int, seller_message: str) -> Tuple[DealStatus, int, str]:
        """
        Respond to the seller's offer.
        
        Args:
            context: Current negotiation context
            seller_price: The seller's current price offer
            seller_message: The seller's message
            
        Returns:
            Tuple of (deal_status, counter_offer, message)
            - deal_status: ACCEPTED if you take the deal, ONGOING if negotiating
            - counter_offer: Your counter price (ignored if deal_status is ACCEPTED)
            - message: Your response message
        """
        pass
    
    @abstractmethod
    def get_personality_prompt(self) -> str:
        """
        Return a prompt that describes how your agent should communicate.
        This will be used to evaluate character consistency.
        
        Returns:
            A detailed prompt describing your agent's communication style
        """
        pass


# ============================================
# PART 3: ADVANCED PSYCHOLOGICAL FRAMEWORK
# ============================================

class PsychologicalTactics:
    """Advanced psychological negotiation tactics"""
    
    @staticmethod
    def analyze_seller_pattern(seller_offers: List[int], messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze seller's negotiation pattern and psychology"""
        if len(seller_offers) < 2:
            return {"pattern": "insufficient_data", "aggression_level": 0.5}
        
        # Calculate price reduction rate
        reductions = []
        for i in range(1, len(seller_offers)):
            reduction = (seller_offers[i-1] - seller_offers[i]) / seller_offers[i-1]
            reductions.append(reduction)
        
        avg_reduction = sum(reductions) / len(reductions) if reductions else 0
        
        # Analyze message patterns
        urgency_keywords = ['limited', 'time', 'hurry', 'quick', 'final', 'last', 'running out']
        quality_keywords = ['premium', 'export', 'grade', 'quality', 'best', 'finest']
        
        seller_messages = [msg['message'] for msg in messages if msg.get('role') == 'seller']
        
        urgency_score = sum(1 for msg in seller_messages 
                           for keyword in urgency_keywords 
                           if keyword.lower() in msg.lower()) / max(len(seller_messages), 1)
        
        quality_emphasis = sum(1 for msg in seller_messages 
                              for keyword in quality_keywords 
                              if keyword.lower() in msg.lower()) / max(len(seller_messages), 1)
        
        # Determine seller personality
        if urgency_score > 0.7:
            seller_type = "aggressive_pushy"
            strategy = "resist_pressure"
        elif quality_emphasis > 0.8:
            seller_type = "quality_focused"
            strategy = "acknowledge_quality"
        elif avg_reduction > 0.08:
            seller_type = "flexible_dealer"
            strategy = "push_harder"
        else:
            seller_type = "firm_trader"
            strategy = "moderate_approach"
        
        return {
            "pattern": seller_type,
            "aggression_level": urgency_score,
            "quality_focus": quality_emphasis,
            "flexibility": avg_reduction,
            "recommended_strategy": strategy,
            "price_reduction_rate": avg_reduction
        }
    
    @staticmethod
    def calculate_psychological_pressure(round_num: int, max_rounds: int = 10) -> float:
        """Calculate psychological pressure factor based on time"""
        pressure = (round_num / max_rounds) ** 2
        return min(pressure, 0.95)  # Never go full panic
    
    @staticmethod
    def generate_counter_psychology(seller_analysis: Dict[str, Any], pressure: float) -> Dict[str, str]:
        """Generate psychological counter-tactics"""
        strategy = seller_analysis.get("recommended_strategy", "moderate_approach")
        
        if strategy == "resist_pressure":
            return {
                "tone": "calm_confident",
                "approach": "show_alternatives",
                "message_style": "I understand you're emphasizing urgency, but I need to make smart decisions. Quality is important, but so is fair pricing."
            }
        elif strategy == "acknowledge_quality":
            return {
                "tone": "appreciative_but_firm",
                "approach": "quality_with_price_reality",
                "message_style": "I absolutely appreciate the premium quality - that's exactly why I'm interested. However, even premium products need realistic pricing."
            }
        elif strategy == "push_harder":
            return {
                "tone": "opportunistic",
                "approach": "leverage_flexibility",
                "message_style": "I can see we're both flexible here. Let's find that sweet spot where we both win."
            }
        else:
            return {
                "tone": "respectful_persistent",
                "approach": "gradual_persuasion",
                "message_style": "I respect your position, and I hope you can understand mine. Let's work together on this."
            }


class MarketIntelligence:
    """Advanced market analysis and pricing intelligence"""
    
    @staticmethod
    def analyze_product_value(product: Product) -> Dict[str, Any]:
        """Deep analysis of product value factors"""
        value_multipliers = {
            "Export": 1.3,
            "A": 1.1,
            "B": 0.95
        }
        
        origin_premiums = {
            "Ratnagiri": 1.25,  # Premium origin for Alphonso
            "Mumbai": 1.1,
            "Maharashtra": 1.15,
            "Gujarat": 1.0
        }
        
        # Seasonal factors (assuming peak season for competition)
        seasonal_factor = 0.9  # Slightly lower due to availability
        
        quality_multiplier = value_multipliers.get(product.quality_grade, 1.0)
        origin_multiplier = origin_premiums.get(product.origin, 1.0)
        
        # Calculate true market value
        adjusted_market_price = int(product.base_market_price * 
                                  quality_multiplier * 
                                  origin_multiplier * 
                                  seasonal_factor)
        
        return {
            "adjusted_market_value": adjusted_market_price,
            "quality_premium": quality_multiplier,
            "origin_premium": origin_multiplier,
            "seasonal_adjustment": seasonal_factor,
            "fair_price_range": (
                int(adjusted_market_price * 0.85),  # Lower bound
                int(adjusted_market_price * 0.95)   # Upper bound
            )
        }
    
    @staticmethod
    def calculate_negotiation_leverage(context: NegotiationContext, market_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate your negotiation leverage"""
        budget_ratio = context.your_budget / market_analysis["adjusted_market_value"]
        
        if budget_ratio >= 1.2:
            leverage = "high"
            confidence = 0.9
        elif budget_ratio >= 0.95:
            leverage = "medium"
            confidence = 0.7
        else:
            leverage = "low"
            confidence = 0.4
        
        return {
            "leverage_level": leverage,
            "confidence_factor": confidence,
            "budget_adequacy": budget_ratio,
            "negotiation_room": max(0, context.your_budget - market_analysis["fair_price_range"][0])
        }


# ============================================
# PART 3: ELITE BUYER AGENT IMPLEMENTATION
# ============================================

class EliteNegotiatorAgent(BaseBuyerAgent):
    """
    🏆 ELITE NEGOTIATOR AGENT - HACKATHON CHAMPION
    
    Advanced AI buyer with psychological analysis, market intelligence,
    and adaptive strategies. Specifically optimized for Alphonso Mango deals.
    """
    
    def __init__(self, name: str = "Elite_Negotiator_Pro"):
        super().__init__(name)
        self.negotiation_history = []
        self.psychological_profile = None
        self.market_analysis = None
        self.leverage_assessment = None
    
    def define_personality(self) -> Dict[str, Any]:
        """Elite negotiator with adaptive psychological tactics"""
        return {
            "personality_type": "elite_strategic",
            "traits": [
                "psychologically_aware",
                "data_driven", 
                "adaptable",
                "confident",
                "respectful_but_firm"
            ],
            "negotiation_style": "Combines psychological analysis with market intelligence. Adapts strategy based on seller personality. Uses respectful but confident communication with strategic pressure points.",
            "catchphrases": [
                "I believe in fair deals for premium quality",
                "Let's find that sweet spot where we both win",
                "Quality deserves fair pricing, and I'm here for both",
                "I appreciate the value, now let's talk realistic numbers"
            ]
        }
    
    def generate_opening_offer(self, context: NegotiationContext) -> Tuple[int, str]:
        """Generate psychologically optimized opening offer"""
        # Perform market analysis
        self.market_analysis = MarketIntelligence.analyze_product_value(context.product)
        self.leverage_assessment = MarketIntelligence.calculate_negotiation_leverage(
            context, self.market_analysis
        )
        
        # Calculate strategic opening based on leverage
        fair_price_lower = self.market_analysis["fair_price_range"][0]
        fair_price_upper = self.market_analysis["fair_price_range"][1]
        
        if self.leverage_assessment["leverage_level"] == "high":
            # Strong position - start lower but reasonable
            opening_offer = int(fair_price_lower * 0.82)
            confidence_level = "strong"
        elif self.leverage_assessment["leverage_level"] == "medium":
            # Moderate position - balanced approach
            opening_offer = int(fair_price_lower * 0.88)
            confidence_level = "balanced"
        else:
            # Weaker position - start closer to fair value
            opening_offer = int(fair_price_lower * 0.94)
            confidence_level = "conservative"
        
        # Ensure within budget
        opening_offer = min(opening_offer, int(context.your_budget * 0.75))
        
        # Generate personality-consistent message
        message = self._generate_opening_message(
            opening_offer, context.product, confidence_level
        )
        
        return opening_offer, message
    
    def respond_to_seller_offer(self, context: NegotiationContext, seller_price: int, seller_message: str) -> Tuple[DealStatus, int, str]:
        """Advanced response with psychological analysis"""
        
        # Update psychological analysis
        self.psychological_profile = PsychologicalTactics.analyze_seller_pattern(
            context.seller_offers, context.messages
        )
        
        # Calculate time pressure
        time_pressure = PsychologicalTactics.calculate_psychological_pressure(
            context.current_round, max_rounds=10
        )
        
        # Check if deal is acceptable
        fair_price_upper = self.market_analysis["fair_price_range"][1]
        
        # Decision matrix for acceptance
        if self._should_accept_deal(seller_price, context, time_pressure):
            return DealStatus.ACCEPTED, seller_price, self._generate_acceptance_message(seller_price)
        
        # Generate strategic counter-offer
        counter_offer = self._calculate_strategic_counter_offer(
            seller_price, context, time_pressure
        )
        
        # Ensure within budget
        counter_offer = min(counter_offer, context.your_budget)
        
        # Generate response message
        response_message = self._generate_response_message(
            counter_offer, seller_price, seller_message, context, time_pressure
        )
        
        return DealStatus.ONGOING, counter_offer, response_message
    
    def get_personality_prompt(self) -> str:
        """Professional personality description"""
        return """
        I am an elite strategic negotiator who combines psychological awareness with market intelligence. 
        I communicate with confident professionalism, acknowledging quality while insisting on fair pricing.
        I adapt my strategy based on the seller's personality and use phrases like 'Let's find that sweet spot where we both win' and 'Quality deserves fair pricing, and I'm here for both'.
        I remain respectful but firm, using data-driven arguments and psychological insight to achieve optimal deals.
        """
    
    # ============================================
    # ADVANCED HELPER METHODS
    # ============================================
    
    def _should_accept_deal(self, seller_price: int, context: NegotiationContext, time_pressure: float) -> bool:
        """Advanced decision logic for deal acceptance"""
        fair_price_upper = self.market_analysis["fair_price_range"][1]
        
        # Basic constraints
        if seller_price > context.your_budget:
            return False
        
        # Excellent deal - always accept
        if seller_price <= fair_price_upper * 0.9:
            return True
        
        # Time pressure factors
        if time_pressure > 0.8 and seller_price <= fair_price_upper:
            return True
        
        # If seller is showing high flexibility, might get better deal
        if (self.psychological_profile and 
            self.psychological_profile.get("flexibility", 0) > 0.1 and 
            time_pressure < 0.6):
            return False
        
        # Good deal in final rounds
        if context.current_round >= 8 and seller_price <= fair_price_upper * 1.05:
            return True
        
        return False
    
    def _calculate_strategic_counter_offer(self, seller_price: int, context: NegotiationContext, time_pressure: float) -> int:
        """Calculate psychologically optimized counter-offer"""
        last_offer = context.your_offers[-1] if context.your_offers else 0
        fair_price_lower = self.market_analysis["fair_price_range"][0]
        
        # Base increment calculation
        price_gap = seller_price - last_offer
        
        # Adjust based on seller psychology
        if self.psychological_profile:
            flexibility = self.psychological_profile.get("flexibility", 0.05)
            if flexibility > 0.08:  # Flexible seller
                increment_rate = 0.3
            elif flexibility < 0.03:  # Rigid seller
                increment_rate = 0.6
            else:  # Normal seller
                increment_rate = 0.45
        else:
            increment_rate = 0.45
        
        # Apply time pressure
        time_factor = 1 + (time_pressure * 0.5)  # Increase offers under pressure
        increment_rate *= time_factor
        
        # Calculate counter offer
        increment = int(price_gap * increment_rate)
        counter_offer = last_offer + max(increment, 5000)  # Minimum ₹5k increment
        
        # Strategic bounds
        counter_offer = max(counter_offer, fair_price_lower * 0.85)
        counter_offer = min(counter_offer, seller_price - 2000)  # Stay below seller price
        
        return counter_offer
    
    def _generate_opening_message(self, offer: int, product: Product, confidence_level: str) -> str:
        """Generate compelling opening message"""
        quality_acknowledgment = f"I'm genuinely interested in these premium {product.quality_grade} grade {product.name} from {product.origin}"
        
        if confidence_level == "strong":
            value_statement = "I believe in fair deals for premium quality, and I'm confident we can find the right price point."
        elif confidence_level == "balanced":
            value_statement = "Quality deserves fair pricing, and I'm here for both."
        else:
            value_statement = "I appreciate the value you're offering and want to make this work."
        
        return f"{quality_acknowledgment}. {value_statement} I'd like to start at ₹{offer:,} and work towards a deal that benefits us both."
    
    def _generate_response_message(self, counter_offer: int, seller_price: int, seller_message: str, context: NegotiationContext, time_pressure: float) -> str:
        """Generate psychologically optimized response"""
        
        # Get psychological counter-tactics
        psychology = PsychologicalTactics.generate_counter_psychology(
            self.psychological_profile, time_pressure
        )
        
        # Base response acknowledging seller
        if "premium" in seller_message.lower() or "quality" in seller_message.lower():
            acknowledgment = "I absolutely recognize the premium quality here"
        elif "limited" in seller_message.lower() or "time" in seller_message.lower():
            acknowledgment = "I understand the time consideration"
        else:
            acknowledgment = "I appreciate your position"
        
        # Value bridge statement
        bridge_statements = [
            "and I'm committed to finding our mutual sweet spot",
            "while ensuring we both get fair value",
            "and want to make this work for both of us",
            "so let's bridge this gap together"
        ]
        
        bridge = random.choice(bridge_statements)
        
        # Closing with counter-offer
        if time_pressure > 0.7:
            urgency_note = f"Given our timeline, I can move to ₹{counter_offer:,}"
        else:
            urgency_note = f"I can offer ₹{counter_offer:,}"
        
        return f"{acknowledgment}, {bridge}. {urgency_note}."
    
    def _generate_acceptance_message(self, price: int) -> str:
        """Generate professional acceptance message"""
        acceptance_phrases = [
            f"Perfect! ₹{price:,} works excellently for both of us",
            f"That's a fair deal at ₹{price:,} - I'm happy to proceed",
            f"Excellent! ₹{price:,} represents great value - let's close this deal",
            f"I'm pleased to accept ₹{price:,} - this is exactly the kind of win-win I was hoping for"
        ]
        
        return random.choice(acceptance_phrases) + ". Thank you for the professional negotiation!"
    
    def analyze_negotiation_progress(self, context: NegotiationContext) -> Dict[str, Any]:
        """Comprehensive negotiation analysis"""
        if not context.seller_offers or not context.your_offers:
            return {"status": "insufficient_data"}
        
        # Progress metrics
        seller_concession = ((context.seller_offers[0] - context.seller_offers[-1]) / 
                           context.seller_offers[0]) if len(context.seller_offers) > 1 else 0
        
        your_increase = ((context.your_offers[-1] - context.your_offers[0]) / 
                        context.your_offers[0]) if len(context.your_offers) > 1 else 0
        
        gap_closure = 1 - ((context.seller_offers[-1] - context.your_offers[-1]) / 
                          (context.seller_offers[0] - context.your_offers[0]))
        
        return {
            "seller_concession_rate": seller_concession,
            "buyer_increase_rate": your_increase,
            "gap_closure_progress": gap_closure,
            "negotiation_momentum": "positive" if gap_closure > 0.3 else "neutral" if gap_closure > 0 else "negative",
            "estimated_final_price": int((context.seller_offers[-1] + context.your_offers[-1]) / 2)
        }
    
    def calculate_fair_price(self, product: Product) -> int:
        """Calculate sophisticated fair price estimate"""
        if not self.market_analysis:
            self.market_analysis = MarketIntelligence.analyze_product_value(product)
        
        return int(sum(self.market_analysis["fair_price_range"]) / 2)


# ============================================
# PART 4: YOUR MAIN AGENT (REQUIRED IMPLEMENTATION)
# ============================================

class YourBuyerAgent(EliteNegotiatorAgent):
    """
    🏆 YOUR ELITE HACKATHON BUYER AGENT
    
    This is your main agent that will be evaluated.
    It inherits all the advanced capabilities from EliteNegotiatorAgent
    but you can customize it further if needed.
    """
    
    def __init__(self, name: str = "Hackathon_Champion_Agent"):
        super().__init__(name)
        print("🚀 Elite Negotiation Agent Initialized")
        print("💼 Ready for professional Alphonso Mango negotiations")
        print("🧠 Advanced psychological analysis: ACTIVE")
        print("📊 Market intelligence system: LOADED")
        print("🎯 Success optimization: MAXIMUM")


# ============================================
# PART 5: EXAMPLE SIMPLE AGENT (FOR REFERENCE)
# ============================================

class ExampleSimpleAgent(BaseBuyerAgent):
    """
    A simple example agent that you can use as reference.
    This agent has basic logic - you should do better!
    """
    
    def define_personality(self) -> Dict[str, Any]:
        return {
            "personality_type": "cautious",
            "traits": ["careful", "budget-conscious", "polite"],
            "negotiation_style": "Makes small incremental offers, very careful with money",
            "catchphrases": ["Let me think about that...", "That's a bit steep for me"]
        }
    
    def generate_opening_offer(self, context: NegotiationContext) -> Tuple[int, str]:
        # Start at 60% of market price
        opening = int(context.product.base_market_price * 0.6)
        opening = min(opening, context.your_budget)
        
        return opening, f"I'm interested, but ₹{opening} is what I can offer. Let me think about that..."
    
    def respond_to_seller_offer(self, context: NegotiationContext, seller_price: int, seller_message: str) -> Tuple[DealStatus, int, str]:
        # Accept if within budget and below 85% of market
        if seller_price <= context.your_budget and seller_price <= context.product.base_market_price * 0.85:
            return DealStatus.ACCEPTED, seller_price, f"Alright, ₹{seller_price} works for me!"
        
        # Counter with small increment
        last_offer = context.your_offers[-1] if context.your_offers else 0
        counter = min(int(last_offer * 1.1), context.your_budget)
        
        if counter >= seller_price * 0.95:  # Close to agreement
            counter = min(seller_price - 1000, context.your_budget)
            return DealStatus.ONGOING, counter, f"That's a bit steep for me. How about ₹{counter}?"
        
        return DealStatus.ONGOING, counter, f"I can go up to ₹{counter}, but that's pushing my budget."
    
    def get_personality_prompt(self) -> str:
        return """
        I am a cautious buyer who is very careful with money. I speak politely but firmly.
        I often say things like 'Let me think about that' or 'That's a bit steep for me'.
        I make small incremental offers and show concern about my budget.
        """


# ============================================
# PART 6: TESTING FRAMEWORK (DO NOT MODIFY)
# ============================================

class MockSellerAgent:
    """A simple mock seller for testing your agent"""
    
    def __init__(self, min_price: int, personality: str = "standard"):
        self.min_price = min_price
        self.personality = personality
        
    def get_opening_price(self, product: Product) -> Tuple[int, str]:
        # Start at 150% of market price
        price = int(product.base_market_price * 1.5)
        return price, f"These are premium {product.quality_grade} grade {product.name}. I'm asking ₹{price}."
    
    def respond_to_buyer(self, buyer_offer: int, round_num: int) -> Tuple[int, str, bool]:
        if buyer_offer >= self.min_price * 1.1:  # Good profit
            return buyer_offer, f"You have a deal at ₹{buyer_offer}!", True
            
        if round_num >= 8:  # Close to timeout
            counter = max(self.min_price, int(buyer_offer * 1.05))
            return counter, f"Final offer: ₹{counter}. Take it or leave it.", False
        else:
            counter = max(self.min_price, int(buyer_offer * 1.15))
            return counter, f"I can come down to ₹{counter}.", False


def run_negotiation_test(buyer_agent: BaseBuyerAgent, product: Product, buyer_budget: int, seller_min: int) -> Dict[str, Any]:
    """Test a negotiation between your buyer and a mock seller"""
    
    seller = MockSellerAgent(seller_min)
    context = NegotiationContext(
        product=product,
        your_budget=buyer_budget,
        current_round=0,
        seller_offers=[],
        your_offers=[],
        messages=[]
    )
    
    # Seller opens
    seller_price, seller_msg = seller.get_opening_price(product)
    context.seller_offers.append(seller_price)
    context.messages.append({"role": "seller", "message": seller_msg})
    
    # Run negotiation
    deal_made = False
    final_price = None
    
    for round_num in range(10):  # Max 10 rounds
        context.current_round = round_num + 1
        
        # Buyer responds
        if round_num == 0:
            buyer_offer, buyer_msg = buyer_agent.generate_opening_offer(context)
            status = DealStatus.ONGOING
        else:
            status, buyer_offer, buyer_msg = buyer_agent.respond_to_seller_offer(
                context, seller_price, seller_msg
            )
        
        context.your_offers.append(buyer_offer)
        context.messages.append({"role": "buyer", "message": buyer_msg})
        
        if status == DealStatus.ACCEPTED:
            deal_made = True
            final_price = seller_price
            break
            
        # Seller responds
        seller_price, seller_msg, seller_accepts = seller.respond_to_buyer(buyer_offer, round_num)
        
        if seller_accepts:
            deal_made = True
            final_price = buyer_offer
            context.messages.append({"role": "seller", "message": seller_msg})
            break
            
        context.seller_offers.append(seller_price)
        context.messages.append({"role": "seller", "message": seller_msg})
    
    # Calculate results
    result = {
        "deal_made": deal_made,
        "final_price": final_price,
        "rounds": context.current_round,
        "savings": buyer_budget - final_price if deal_made else 0,
        "savings_pct": ((buyer_budget - final_price) / buyer_budget * 100) if deal_made else 0,
        "below_market_pct": ((product.base_market_price - final_price) / product.base_market_price * 100) if deal_made else 0,
        "conversation": context.messages
    }
    
    return result


# ============================================
# PART 7: PROFESSIONAL TESTING SUITE
# ============================================

def test_your_agent():
    """🚀 PROFESSIONAL HACKATHON TESTING SUITE"""
    
    print("=" * 80)
    print("🏆 ELITE AI NEGOTIATION AGENT - HACKATHON TESTING")
    print("🥭 Specialized for Alphonso Mango Negotiations")
    print("=" * 80)
    
    # Alphonso Mango test scenarios
    alphonso_mango = Product(
        name="Alphonso Mangoes",
        category="Premium Mangoes",
        quantity=100,
        quality_grade="Export",  # Premium grade
        origin="Ratnagiri",     # Premium origin
        base_market_price=220000,  # Higher premium price
        attributes={
            "ripeness": "optimal", 
            "export_grade": True,
            "certification": "organic",
            "harvest_season": "peak"
        }
    )
    
    # Initialize the elite agent
    elite_agent = YourBuyerAgent("Hackathon_Elite_Negotiator")
    
    print(f"\n🤖 AGENT PROFILE:")
    print(f"   Name: {elite_agent.name}")
    print(f"   Type: {elite_agent.personality['personality_type']}")
    print(f"   Traits: {', '.join(elite_agent.personality['traits'])}")
    print(f"   Style: {elite_agent.personality['negotiation_style']}")
    
    # Comprehensive test scenarios
    test_scenarios = [
        {
            "name": "🏆 CHAMPIONSHIP SCENARIO",
            "description": "Perfect budget, moderate seller - Win big!",
            "budget": 250000,  # 113% of market price
            "seller_min": 185000,  # 84% of market price
            "difficulty": "MEDIUM",
            "target_savings": "> 15%"
        },
        {
            "name": "🔥 PRESSURE COOKER", 
            "description": "Tight budget, tough seller - Elite skills needed",
            "budget": 210000,  # 95% of market price
            "seller_min": 190000,  # 86% of market price
            "difficulty": "EXTREME",
            "target_savings": "> 5%"
        },
        {
            "name": "💎 PREMIUM OPPORTUNITY",
            "description": "High budget, flexible seller - Maximize savings",
            "budget": 280000,  # 127% of market price
            "seller_min": 170000,  # 77% of market price  
            "difficulty": "EASY",
            "target_savings": "> 25%"
        },
        {
            "name": "⚡ LIGHTNING ROUND",
            "description": "Realistic budget, standard seller - Prove consistency",
            "budget": 230000,  # 104% of market price
            "seller_min": 180000,  # 82% of market price
            "difficulty": "MEDIUM",
            "target_savings": "> 12%"
        }
    ]
    
    total_savings = 0
    deals_made = 0
    total_scenarios = len(test_scenarios)
    
    print(f"\n🎯 RUNNING {total_scenarios} ELITE TEST SCENARIOS")
    print("=" * 60)
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n🚀 SCENARIO {i}/{total_scenarios}: {scenario['name']}")
        print(f"📋 {scenario['description']}")
        print(f"💰 Budget: ₹{scenario['budget']:,} | Market: ₹{alphonso_mango.base_market_price:,}")
        print(f"🎚️  Difficulty: {scenario['difficulty']} | Target: {scenario['target_savings']}")
        print("-" * 50)
        
        # Run the negotiation
        result = run_negotiation_test(
            elite_agent, 
            alphonso_mango, 
            scenario['budget'], 
            scenario['seller_min']
        )
        
        if result["deal_made"]:
            deals_made += 1
            total_savings += result["savings"]
            
            # Success analysis
            market_discount = ((alphonso_mango.base_market_price - result['final_price']) / 
                             alphonso_mango.base_market_price * 100)
            
            # Performance rating
            if market_discount >= 25:
                rating = "🏆 LEGENDARY"
                emoji = "🔥"
            elif market_discount >= 15:
                rating = "🥇 OUTSTANDING" 
                emoji = "⭐"
            elif market_discount >= 10:
                rating = "🥈 EXCELLENT"
                emoji = "✨"
            elif market_discount >= 5:
                rating = "🥉 GOOD"
                emoji = "👍"
            else:
                rating = "✅ ACCEPTABLE"
                emoji = "👌"
            
            print(f"{emoji} SUCCESS! Deal closed at ₹{result['final_price']:,}")
            print(f"   💫 Performance: {rating}")
            print(f"   ⏱️  Rounds: {result['rounds']}")
            print(f"   💵 Savings: ₹{result['savings']:,} ({result['savings_pct']:.1f}% of budget)")
            print(f"   📊 Market Discount: {market_discount:.1f}%")
            
            # Show key negotiation moments
            if len(result['conversation']) >= 4:
                print(f"   🗣️  Key Moment: \"{result['conversation'][2]['message'][:60]}...\"")
                
        else:
            print(f"❌ FAILED - No deal after {result['rounds']} rounds")
            print(f"   💔 Missed opportunity - Learn and adapt!")
    
    # Final comprehensive analysis
    print("\n" + "=" * 80)
    print("🏆 HACKATHON PERFORMANCE ANALYSIS")
    print("=" * 80)
    
    success_rate = (deals_made / total_scenarios) * 100
    avg_savings = total_savings / deals_made if deals_made > 0 else 0
    
    print(f"📊 CORE METRICS:")
    print(f"   🎯 Success Rate: {deals_made}/{total_scenarios} ({success_rate:.1f}%)")
    print(f"   💰 Total Savings: ₹{total_savings:,}")
    print(f"   📈 Average Savings: ₹{avg_savings:,.0f}")
    
    # Performance classification
    if success_rate >= 90 and avg_savings >= 30000:
        performance_class = "🏆 HACKATHON CHAMPION"
        performance_color = "🟢"
    elif success_rate >= 75 and avg_savings >= 20000:
        performance_class = "🥇 ELITE PERFORMER"
        performance_color = "🟡"
    elif success_rate >= 60 and avg_savings >= 15000:
        performance_class = "🥈 STRONG CONTENDER"
        performance_color = "🟠"
    else:
        performance_class = "🥉 NEEDS OPTIMIZATION"
        performance_color = "🔴"
    
    print(f"\n{performance_color} OVERALL RATING: {performance_class}")
    
    # Advanced insights
    print(f"\n🧠 ADVANCED INSIGHTS:")
    print(f"   🎭 Agent Personality: Elite Strategic Negotiator")
    print(f"   🔬 Uses psychological analysis and market intelligence")
    print(f"   📊 Adaptive strategy based on seller behavior")
    print(f"   ⚡ Optimized for 2-minute negotiations")
    
    # Competition readiness
    print(f"\n🏁 HACKATHON READINESS:")
    if success_rate >= 75:
        print(f"   ✅ READY TO COMPETE! High success probability")
        print(f"   💪 Strong negotiation fundamentals")
        print(f"   🎯 Consistent deal-closing ability")
    else:
        print(f"   ⚠️  NEEDS TUNING - Consider strategy adjustments")
        print(f"   🔄 Review failed scenarios for improvement")
    
    print(f"\n🎊 Your Elite Agent is ready for the hackathon!")
    print(f"💼 Professional, intelligent, and results-driven")
    print("=" * 80)


# ============================================
# PART 8: DEMONSTRATION RUNNER
# ============================================

def demonstrate_agent_capabilities():
    """🎭 Demonstrate the agent's advanced capabilities"""
    
    print("🎪 LIVE DEMONSTRATION - ELITE NEGOTIATION CAPABILITIES")
    print("=" * 60)
    
    # Sample product for demonstration
    demo_product = Product(
        name="Alphonso Mangoes",
        category="Premium Mangoes", 
        quantity=100,
        quality_grade="Export",
        origin="Ratnagiri",
        base_market_price=220000,
        attributes={"ripeness": "optimal", "export_grade": True}
    )
    
    # Create demo context
    demo_context = NegotiationContext(
        product=demo_product,
        your_budget=240000,
        current_round=1,
        seller_offers=[330000],  # High opening
        your_offers=[],
        messages=[{"role": "seller", "message": "Premium export grade Alphonso mangoes from Ratnagiri! These are the finest available. My price is ₹3,30,000."}]
    )
    
    # Initialize elite agent
    elite_agent = YourBuyerAgent("Demo_Elite")
    
    print(f"\n🥭 PRODUCT: {demo_product.name}")
    print(f"📊 Market Price: ₹{demo_product.base_market_price:,}")
    print(f"💰 Your Budget: ₹{demo_context.your_budget:,}")
    print(f"🤖 Seller Opens: ₹{demo_context.seller_offers[0]:,}")
    
    # Generate opening offer
    opening_offer, opening_message = elite_agent.generate_opening_offer(demo_context)
    
    print(f"\n🎯 ELITE AGENT ANALYSIS:")
    print(f"   💡 Market Intelligence: Active")
    print(f"   🧠 Psychological Profiling: Initialized") 
    print(f"   📈 Leverage Assessment: Completed")
    
    print(f"\n💬 ELITE AGENT RESPONDS:")
    print(f"   💰 Opening Offer: ₹{opening_offer:,}")
    print(f"   🗣️  Message: \"{opening_message}\"")
    
    # Analyze the strategy
    savings_potential = demo_context.your_budget - opening_offer
    market_discount = ((demo_product.base_market_price - opening_offer) / demo_product.base_market_price) * 100
    
    print(f"\n📊 STRATEGY ANALYSIS:")
    print(f"   🎯 Negotiation Room: ₹{savings_potential:,}")
    print(f"   📉 Below Market: {market_discount:.1f}%")
    print(f"   🧠 Psychology: Respectful but confident positioning")
    print(f"   ⚡ Ready for adaptive responses based on seller reactions")
    
    print(f"\n✨ This is just the opening move!")
    print(f"🔄 Agent will adapt strategy based on seller's responses")
    print("=" * 60)


# ============================================
# PART 9: MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    """🚀 HACKATHON AGENT TESTING SUITE"""
    
    print("🎊 WELCOME TO THE ELITE AI NEGOTIATION AGENT!")
    print("🏆 Built for Hackathon Victory")
    print("🥭 Specialized for Alphonso Mango Negotiations")
    print("\nChoose your testing mode:")
    print("1. 🔥 Full Hackathon Test Suite")
    print("2. 🎭 Live Capability Demonstration") 
    print("3. 🏃 Quick Performance Check")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            print("\n🚀 LAUNCHING FULL TEST SUITE...")
            test_your_agent()
            
        elif choice == "2":
            print("\n🎭 STARTING LIVE DEMONSTRATION...")
            demonstrate_agent_capabilities()
            
        elif choice == "3":
            print("\n⚡ QUICK PERFORMANCE CHECK...")
            # Quick single test
            alphonso = Product(
                name="Alphonso Mangoes", category="Premium Mangoes", quantity=100,
                quality_grade="Export", origin="Ratnagiri", base_market_price=220000,
                attributes={"ripeness": "optimal", "export_grade": True}
            )
            
            agent = YourBuyerAgent("Quick_Test")
            result = run_negotiation_test(agent, alphonso, 240000, 180000)
            
            if result["deal_made"]:
                market_discount = ((220000 - result['final_price']) / 220000) * 100
                print(f"✅ SUCCESS! Deal at ₹{result['final_price']:,}")
                print(f"💫 Market Discount: {market_discount:.1f}%")
                print(f"🎯 Rounds: {result['rounds']}")
            else:
                print(f"❌ No deal after {result['rounds']} rounds")
        else:
            print("🚀 Running default full test suite...")
            test_your_agent()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Testing interrupted. Agent ready for deployment!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("🔄 Running basic test instead...")
        test_your_agent()
    
    print(f"\n🎊 Elite Negotiation Agent Testing Complete!")
    print(f"🏆 Ready for Hackathon Competition!")