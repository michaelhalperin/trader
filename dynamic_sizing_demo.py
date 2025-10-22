#!/usr/bin/env python3
"""
Demo of the new dynamic trade sizing system
"""

def calculate_trade_size(account_balance, trade_size_pct=0.05, max_trade=100, min_trade=10):
    """Calculate dynamic trade size based on account balance"""
    
    # Calculate trade size as percentage of account
    calculated_size = account_balance * trade_size_pct
    
    # Apply min/max limits
    final_size = max(min_trade, min(calculated_size, max_trade))
    
    return final_size, calculated_size

def demo_dynamic_sizing():
    """Demonstrate how the new dynamic sizing works"""
    
    print("🎯 DYNAMIC TRADE SIZING DEMO")
    print("=" * 50)
    print()
    
    # Different account sizes
    account_sizes = [100, 500, 1000, 5000, 10000, 50000, 100000]
    
    print("📊 TRADE SIZE CALCULATIONS:")
    print("Account Size | 5% Trade | Final Size | Reason")
    print("-" * 55)
    
    for balance in account_sizes:
        final_size, calculated = calculate_trade_size(balance)
        
        if calculated < 10:
            reason = "Below minimum ($10)"
        elif calculated > 100:
            reason = "Capped at maximum ($100)"
        else:
            reason = "5% of account"
            
        print(f"${balance:>10,} | ${calculated:>7.2f} | ${final_size:>9.2f} | {reason}")
    
    print()
    print("🔧 CONFIGURATION OPTIONS:")
    print("• trade_size_pct: 0.05 (5% of account)")
    print("• max_trade_usd: 100 (maximum per trade)")
    print("• min_trade_usd: 10 (minimum per trade)")
    print()
    print("💡 BENEFITS:")
    print("✅ Scales with your account size")
    print("✅ Never risks too much (max $100)")
    print("✅ Never trades too little (min $10)")
    print("✅ Grows with your profits")
    print("✅ Protects small accounts")

if __name__ == "__main__":
    demo_dynamic_sizing()
