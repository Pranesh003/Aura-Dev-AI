from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import stripe
import os

import database, models, auth, crud

router = APIRouter(
    prefix="/api/billing",
    tags=["Billing"],
)

# You will need to set this in your .env for production
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder")
webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "whsec_placeholder")

@router.post("/checkout")
async def create_checkout_session(current_user: models.User = Depends(auth.get_current_active_user)):
    """ Creates a Stripe Checkout Session for purchasing 50 Aura Credits """
    if stripe.api_key == "sk_test_placeholder":
        # MOCK SYSTEM FOR DEVELOPMENT
        # Automatically add credits if no real Stripe keys are configured
        db = database.SessionLocal()
        try:
            crud.update_user_credits(db, current_user.id, 50)
            return {"url": "http://localhost:5173/dashboard?mock_payment=success"}
        finally:
            db.close()
            
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            client_reference_id=current_user.id,
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': '50 Aura Credits',
                        'description': 'Deploy 5 full 7-Agent Architectures',
                    },
                    'unit_amount': 999, # $9.99
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:5173/dashboard?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://localhost:5173/dashboard?cancel=true',
        )
        return {"url": session.url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """ Listens to the Stripe pipeline for successful transactions """
    if stripe.api_key == "sk_test_placeholder":
        return {"status": "success", "message": "Ignored due to mock configuration"}
        
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        
        user_id = session.get("client_reference_id")
        if user_id:
            db = database.SessionLocal()
            try:
                crud.update_user_credits(db, user_id, 50)
            finally:
                db.close()

    return {"status": "success"}
