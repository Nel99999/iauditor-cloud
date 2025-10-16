"""
Script to activate all inactive organization units and checklist templates
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import os

async def activate_all_items():
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/')
    db_name = os.environ.get('DB_NAME', 'operational_platform')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print('='*100)
    print('ACTIVATING ALL INACTIVE ITEMS')
    print('='*100)
    print()
    
    # Get llewellyn's org
    user = await db.users.find_one({'email': 'llewellyn@bluedawncapital.co.za'})
    org_id = user.get('organization_id')
    
    print(f'Organization: {org_id}')
    print()
    
    # Activate organization units
    print('1. Activating Organization Units...')
    inactive_units = await db.organization_units.count_documents({
        'organization_id': org_id,
        'is_active': False
    })
    
    result = await db.organization_units.update_many(
        {'organization_id': org_id, 'is_active': False},
        {'$set': {'is_active': True, 'updated_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    print(f'   Found {inactive_units} inactive units')
    print(f'   Activated: {result.modified_count} units')
    print()
    
    # Activate checklist templates
    print('2. Activating Checklist Templates...')
    inactive_templates = await db.checklist_templates.count_documents({
        'organization_id': org_id,
        'is_active': False
    })
    
    result = await db.checklist_templates.update_many(
        {'organization_id': org_id, 'is_active': False},
        {'$set': {'is_active': True, 'updated_at': datetime.now(timezone.utc).isoformat()}}
    )
    
    print(f'   Found {inactive_templates} inactive templates')
    print(f'   Activated: {result.modified_count} templates')
    print()
    
    # Verify
    print('='*100)
    print('VERIFICATION')
    print('='*100)
    
    active_units = await db.organization_units.count_documents({
        'organization_id': org_id,
        'is_active': True
    })
    active_templates = await db.checklist_templates.count_documents({
        'organization_id': org_id,
        'is_active': True
    })
    
    print(f'Active Organization Units: {active_units}/40')
    print(f'Active Checklist Templates: {active_templates}/6')
    print()
    
    if active_units == 40:
        print('✅ All organization units are now active')
    else:
        print(f'⚠️  Still have inactive units: {40 - active_units}')
    
    if active_templates == 6:
        print('✅ All checklist templates are now active')
    else:
        print(f'⚠️  Still have inactive templates: {6 - active_templates}')
    
    client.close()

if __name__ == "__main__":
    asyncio.run(activate_all_items())
