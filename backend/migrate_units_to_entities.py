#!/usr/bin/env python3
"""
Migration Script: organizational_units → organizational_entities
Migrates existing organizational units to the new rich entity system
Preserves all data and adds default values for new fields
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, timezone

async def migrate_units_to_entities():
    """Migrate organization_units to organizational_entities"""
    
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'operational_platform')
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    print("="*80)
    print("MIGRATION: organizational_units → organizational_entities")
    print("="*80)
    
    # Get all existing organizational units
    units = await db.organization_units.find({"is_active": True}).to_list(None)
    
    print(f"\n📊 Found {len(units)} organizational units to migrate")
    
    if len(units) == 0:
        print("⚠️  No units to migrate")
        return
    
    # Determine entity type from level
    level_to_type = {
        1: 'profile',
        2: 'organisation',
        3: 'company',
        4: 'branch',
        5: 'brand'
    }
    
    # Level colors
    level_colors = {
        1: '#3b82f6',
        2: '#22c55e',
        3: '#a855f7',
        4: '#f97316',
        5: '#ec4899'
    }
    
    migrated_count = 0
    skipped_count = 0
    
    for unit in units:
        try:
            # Check if already migrated
            existing = await db.organizational_entities.find_one({"id": unit["id"]})
            if existing:
                print(f"⏭️  Skipping {unit['name']} (already migrated)")
                skipped_count += 1
                continue
            
            # Determine entity type from level
            entity_type = level_to_type.get(unit["level"], "profile")
            
            # Create rich entity with defaults for new fields
            entity = {
                "id": unit["id"],
                "organization_id": unit["organization_id"],
                "entity_type": entity_type,
                "level": unit["level"],
                
                # Core fields from old unit
                "name": unit["name"],
                "description": unit.get("description", ""),
                
                # Branding defaults
                "logo_url": None,
                "primary_color": level_colors.get(unit["level"], "#3b82f6"),
                "secondary_color": None,
                
                # Contact & Location defaults
                "address_street": None,
                "address_city": None,
                "address_state": None,
                "address_country": None,
                "address_postal_code": None,
                "phone": None,
                "email": None,
                "website": None,
                
                # Business Details defaults
                "tax_id": None,
                "registration_number": None,
                "established_date": None,
                "industry": None,
                
                # Financial defaults
                "cost_center": None,
                "budget_code": None,
                "currency": "USD",
                
                # Management
                "default_manager_id": None,
                
                # Custom fields
                "custom_fields": {},
                
                # Hierarchy (preserve from old system)
                "parent_id": unit.get("parent_id"),
                
                # Status
                "is_active": unit.get("is_active", True),
                "status": "active" if unit.get("is_active", True) else "inactive",
                
                # Audit
                "created_by": unit.get("created_by", "system"),
                "created_at": unit.get("created_at", datetime.now(timezone.utc)).isoformat() if isinstance(unit.get("created_at"), datetime) else str(unit.get("created_at", datetime.now(timezone.utc).isoformat())),
                "updated_by": unit.get("updated_by"),
                "updated_at": unit.get("updated_at", datetime.now(timezone.utc)).isoformat() if isinstance(unit.get("updated_at"), datetime) else str(unit.get("updated_at", datetime.now(timezone.utc).isoformat())),
            }
            
            # Insert into new collection
            await db.organizational_entities.insert_one(entity)
            
            print(f"✅ Migrated: {unit['name']} (Level {unit['level']}, Type: {entity_type})")
            migrated_count += 1
            
        except Exception as e:
            print(f"❌ Failed to migrate {unit.get('name', 'Unknown')}: {str(e)}")
    
    print("\n" + "="*80)
    print(f"MIGRATION COMPLETE")
    print(f"✅ Migrated: {migrated_count}")
    print(f"⏭️  Skipped: {skipped_count}")
    print(f"📊 Total: {len(units)}")
    print("="*80)
    
    # Verify migration
    print("\n🔍 VERIFICATION:")
    entity_count = await db.organizational_entities.count_documents({"is_active": True})
    print(f"   organizational_entities collection: {entity_count} records")
    print(f"   organization_units collection: {len(units)} records")
    
    if entity_count >= len(units):
        print("✅ Migration successful - all units migrated to entities")
    else:
        print(f"⚠️  Warning: {len(units) - entity_count} units not migrated")
    
    client.close()


if __name__ == "__main__":
    print("\n🚀 Starting migration...\n")
    asyncio.run(migrate_units_to_entities())
    print("\n✅ Migration script completed\n")
