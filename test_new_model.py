#!/usr/bin/env python3
"""
Simple test to check if the new BERT model is accessible
"""

import sys
import os

def test_model_access():
    """Test if the new model can be accessed"""
    print("=== TESTING NEW BERT MODEL ACCESS ===")
    
    try:
        from transformers import AutoTokenizer, AutoModelForTokenClassification
        
        model_name = "LiProject/Bert-turkish-pos-trained"
        print(f"Testing model: {model_name}")
        
        # Test tokenizer access
        print("1. Testing tokenizer access...")
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        print("   ✅ Tokenizer loaded successfully")
        
        # Test model access
        print("2. Testing model access...")
        model = AutoModelForTokenClassification.from_pretrained(model_name)
        print("   ✅ Model loaded successfully")
        
        # Test pipeline creation
        print("3. Testing pipeline creation...")
        from transformers import pipeline
        nlp = pipeline("token-classification", model=model, tokenizer=tokenizer)
        print("   ✅ Pipeline created successfully")
        
        # Test with simple text
        print("4. Testing with sample Turkish text...")
        test_text = "Merhaba dünya"
        result = nlp(test_text)
        print(f"   ✅ Processing result: {result}")
        
        print("\n🎉 SUCCESS: New BERT model is fully accessible!")
        print(f"Model: {model_name}")
        print(f"Tokenizer type: {type(tokenizer)}")
        print(f"Model type: {type(model)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        
        if "gated" in str(e).lower():
            print("\n🔒 MODEL IS GATED")
            print("This model requires authentication to access.")
            print("You need to:")
            print("1. Create a Hugging Face account")
            print("2. Accept the model license")
            print("3. Generate an access token")
            print("4. Login using: huggingface-cli login")
        elif "404" in str(e) or "not found" in str(e).lower():
            print("\n❓ MODEL NOT FOUND")
            print("The model repository may not exist or the name is incorrect.")
        else:
            print("\n❓ OTHER ERROR")
            print("There may be a network issue or the model is temporarily unavailable.")
        
        return False

if __name__ == "__main__":
    test_model_access()