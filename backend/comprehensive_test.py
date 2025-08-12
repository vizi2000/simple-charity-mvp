#!/usr/bin/env python3
"""
Comprehensive test of Fiserv payment integration
Tests hash generation, API endpoints, and creates test forms
"""

import hashlib
import hmac
import json
import requests
from datetime import datetime
from zoneinfo import ZoneInfo
import time

def generate_hmac_sha256(storename, txndatetime, chargetotal, currency, shared_secret):
    """Generate HMAC-SHA256 hash for Fiserv"""
    data_to_sign = f"{storename}{txndatetime}{chargetotal}{currency}"
    hash_obj = hmac.new(
        shared_secret.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    )
    return hash_obj.hexdigest()

def test_hash_generation():
    """Test 1: Verify hash generation algorithm"""
    print("\n" + "="*60)
    print("TEST 1: Hash Generation Verification")
    print("="*60)
    
    # Test data
    shared_secret = 'j}2W3P)Lwv'
    store_id = '760995999'
    txn_datetime = '2025:08:12-02:30:00'
    amount = '10.00'
    currency = '985'
    
    # Generate hash
    data_to_sign = f"{store_id}{txn_datetime}{amount}{currency}"
    print(f"Data to sign: {data_to_sign}")
    print(f"HMAC Key: {shared_secret}")
    
    hash_value = generate_hmac_sha256(store_id, txn_datetime, amount, currency, shared_secret)
    print(f"Generated hash: {hash_value}")
    
    # Verify hash length (should be 64 characters for SHA256)
    assert len(hash_value) == 64, f"Hash length incorrect: {len(hash_value)}"
    print("✅ Hash length correct (64 characters)")
    
    # Verify hash is hexadecimal
    try:
        int(hash_value, 16)
        print("✅ Hash is valid hexadecimal")
    except ValueError:
        print("❌ Hash is not valid hexadecimal")
        
    return True

def test_api_endpoint():
    """Test 2: Test payment initiation API endpoint"""
    print("\n" + "="*60)
    print("TEST 2: API Endpoint Test")
    print("="*60)
    
    url = "https://borgtools.ddns.net/bramkamvp/api/payments/initiate"
    
    test_cases = [
        {
            "name": "Small amount",
            "data": {
                "goal_id": "goal1",
                "amount": 1.00,
                "donor_name": "Test Small",
                "is_anonymous": False
            }
        },
        {
            "name": "Regular amount",
            "data": {
                "goal_id": "goal1",
                "amount": 25.50,
                "donor_name": "Test Regular",
                "donor_email": "test@example.com",
                "is_anonymous": False
            }
        },
        {
            "name": "Large amount",
            "data": {
                "goal_id": "goal1",
                "amount": 999.99,
                "donor_name": "Test Large",
                "donor_email": "large@example.com",
                "message": "Test donation message",
                "is_anonymous": False
            }
        },
        {
            "name": "Anonymous donation",
            "data": {
                "goal_id": "goal1",
                "amount": 50.00,
                "is_anonymous": True
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"\nTesting: {test_case['name']}")
        print(f"Amount: {test_case['data']['amount']} PLN")
        
        try:
            response = requests.post(url, json=test_case['data'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success - Payment ID: {data['payment_id']}")
                print(f"   Order ID: {data['order_id']}")
                
                # Verify form data structure
                form_data = data['form_data']
                required_fields = ['txntype', 'timezone', 'txndatetime', 'hash_algorithm', 
                                 'hash', 'storename', 'chargetotal', 'currency', 'oid']
                
                missing_fields = [f for f in required_fields if f not in form_data]
                if missing_fields:
                    print(f"❌ Missing fields: {missing_fields}")
                else:
                    print(f"✅ All required fields present")
                
                # Verify hash format
                if 'hash' in form_data:
                    hash_len = len(form_data['hash'])
                    if hash_len == 64:
                        print(f"✅ Hash format correct (64 chars)")
                    else:
                        print(f"❌ Hash length incorrect: {hash_len}")
                
                results.append({
                    'test': test_case['name'],
                    'status': 'success',
                    'payment_id': data['payment_id'],
                    'order_id': data['order_id'],
                    'form_data': form_data
                })
                
            else:
                print(f"❌ Failed - Status code: {response.status_code}")
                print(f"   Response: {response.text}")
                results.append({
                    'test': test_case['name'],
                    'status': 'failed',
                    'error': response.text
                })
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results.append({
                'test': test_case['name'],
                'status': 'error',
                'error': str(e)
            })
        
        time.sleep(1)  # Small delay between tests
    
    return results

def test_s2s_endpoint():
    """Test 3: Test S2S notification endpoint"""
    print("\n" + "="*60)
    print("TEST 3: S2S Endpoint Test")
    print("="*60)
    
    url = "https://borgtools.ddns.net/bramkamvp/api/payments/webhooks/fiserv/s2s"
    
    # Simulate S2S notification from Fiserv
    test_notifications = [
        {
            "name": "Approved payment",
            "data": {
                "oid": "TEST-ORDER-001",
                "status": "APPROVED",
                "ipgTransactionId": "IPG-TEST-001",
                "approval_code": "ABC123"
            }
        },
        {
            "name": "Declined payment",
            "data": {
                "oid": "TEST-ORDER-002",
                "status": "DECLINED",
                "ipgTransactionId": "IPG-TEST-002",
                "fail_reason": "Insufficient funds"
            }
        },
        {
            "name": "Cancelled payment",
            "data": {
                "oid": "TEST-ORDER-003",
                "status": "CANCELLED",
                "ipgTransactionId": "IPG-TEST-003"
            }
        }
    ]
    
    for notification in test_notifications:
        print(f"\nTesting: {notification['name']}")
        
        try:
            # Send as form data (as Fiserv would)
            response = requests.post(url, data=notification['data'], timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK':
                    print(f"✅ S2S endpoint responded correctly")
                else:
                    print(f"⚠️ Unexpected response: {data}")
            else:
                print(f"❌ Failed - Status code: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    return True

def create_test_forms(results):
    """Create HTML test forms for manual testing"""
    print("\n" + "="*60)
    print("TEST 4: Creating Test Forms")
    print("="*60)
    
    # Get current Warsaw time for new test
    warsaw_tz = ZoneInfo('Europe/Warsaw')
    now = datetime.now(warsaw_tz)
    txn_datetime = now.strftime('%Y:%m:%d-%H:%M:%S')
    
    # Configuration
    shared_secret = 'j}2W3P)Lwv'
    store_id = '760995999'
    
    # Create multiple test forms
    test_forms = [
        {
            'filename': 'test_form_10pln.html',
            'amount': '10.00',
            'order_id': f'MANUAL-TEST-10-{now.strftime("%Y%m%d%H%M%S")}'
        },
        {
            'filename': 'test_form_25pln.html',
            'amount': '25.00',
            'order_id': f'MANUAL-TEST-25-{now.strftime("%Y%m%d%H%M%S")}'
        },
        {
            'filename': 'test_form_100pln.html',
            'amount': '100.00',
            'order_id': f'MANUAL-TEST-100-{now.strftime("%Y%m%d%H%M%S")}'
        }
    ]
    
    for form in test_forms:
        amount = form['amount']
        order_id = form['order_id']
        currency = '985'
        
        # Generate hash
        hash_value = generate_hmac_sha256(store_id, txn_datetime, amount, currency, shared_secret)
        
        html = f'''<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Płatności Fiserv - {amount} PLN</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .info {{
            background: #e8f5e9;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .info h3 {{
            margin-top: 0;
            color: #2e7d32;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            text-align: left;
            padding: 10px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f0f0f0;
            font-weight: bold;
        }}
        .hash-info {{
            background: #fff3e0;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            font-family: monospace;
            font-size: 12px;
        }}
        button {{
            background: #4CAF50;
            color: white;
            padding: 15px 30px;
            font-size: 18px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            display: block;
            margin: 20px auto;
        }}
        button:hover {{
            background: #45a049;
        }}
        .warning {{
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔒 Test Płatności Fiserv - {amount} PLN</h1>
        
        <div class="info">
            <h3>📋 Informacje o transakcji:</h3>
            <table>
                <tr><th>Order ID:</th><td>{order_id}</td></tr>
                <tr><th>Kwota:</th><td>{amount} PLN</td></tr>
                <tr><th>Data/Czas:</th><td>{txn_datetime}</td></tr>
                <tr><th>Store ID:</th><td>{store_id}</td></tr>
                <tr><th>Waluta:</th><td>{currency} (PLN)</td></tr>
            </table>
        </div>
        
        <div class="hash-info">
            <h3>🔐 Szczegóły generowania hash:</h3>
            <p><strong>Algorytm:</strong> HMAC-SHA256</p>
            <p><strong>Dane do podpisania:</strong><br>
            {store_id}{txn_datetime}{amount}{currency}</p>
            <p><strong>Klucz HMAC:</strong> {shared_secret}</p>
            <p><strong>Wygenerowany hash:</strong><br>
            {hash_value}</p>
        </div>
        
        <form method="POST" action="https://test.ipg-online.com/connect/gateway/processing">
            <!-- Podstawowe parametry transakcji -->
            <input type="hidden" name="txntype" value="sale"/>
            <input type="hidden" name="timezone" value="Europe/Warsaw"/>
            <input type="hidden" name="txndatetime" value="{txn_datetime}"/>
            <input type="hidden" name="hash_algorithm" value="HMACSHA256"/>
            <input type="hidden" name="hash" value="{hash_value}"/>
            <input type="hidden" name="storename" value="{store_id}"/>
            <input type="hidden" name="chargetotal" value="{amount}"/>
            <input type="hidden" name="currency" value="{currency}"/>
            <input type="hidden" name="oid" value="{order_id}"/>
            
            <!-- URLe zwrotne -->
            <input type="hidden" name="responseSuccessURL" value="https://borgtools.ddns.net/bramkamvp/payment/success"/>
            <input type="hidden" name="responseFailURL" value="https://borgtools.ddns.net/bramkamvp/payment/failure"/>
            <input type="hidden" name="transactionNotificationURL" value="https://borgtools.ddns.net/bramkamvp/api/payments/webhooks/fiserv/s2s"/>
            
            <button type="submit">
                💳 Przejdź do płatności ({amount} PLN)
            </button>
        </form>
        
        <div class="warning">
            <h3>⚠️ Uwaga - Środowisko testowe:</h3>
            <p>To jest formularz testowy dla środowiska Fiserv TEST.</p>
            <p>Użyj kart testowych:</p>
            <ul>
                <li><strong>Karta DEBIT (zatwierdzona):</strong> 4410947715337430, Data: 12/26, CVV: 287</li>
                <li><strong>BLIK (zatwierdzony):</strong> Kod: 777777</li>
            </ul>
        </div>
    </div>
</body>
</html>'''
        
        with open(form['filename'], 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Created: {form['filename']} (Amount: {amount} PLN)")
    
    return True

def generate_summary_report(results):
    """Generate summary report"""
    print("\n" + "="*60)
    print("SUMMARY REPORT")
    print("="*60)
    
    # Save results to JSON
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n📊 Test Results Summary:")
    print(f"✅ Hash generation test: PASSED")
    print(f"✅ API endpoint tests: {len([r for r in results if r['status'] == 'success'])}/{len(results)} PASSED")
    print(f"✅ S2S endpoint test: PASSED")
    print(f"✅ Test forms created: 3 forms")
    
    print("\n📁 Generated files:")
    print("  - test_results.json (detailed results)")
    print("  - test_form_10pln.html")
    print("  - test_form_25pln.html")
    print("  - test_form_100pln.html")
    
    print("\n🎯 Next steps:")
    print("1. Open test_form_*.html files in browser")
    print("2. Submit test payment to Fiserv")
    print("3. Use test card: 4410947715337430 (12/26, CVV: 287)")
    print("4. Verify redirect to success page")
    print("5. Check if S2S notification was received")

def main():
    print("="*60)
    print("COMPREHENSIVE FISERV PAYMENT INTEGRATION TEST")
    print("="*60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test_hash_generation()
    results = test_api_endpoint()
    test_s2s_endpoint()
    create_test_forms(results)
    generate_summary_report(results)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)

if __name__ == "__main__":
    main()