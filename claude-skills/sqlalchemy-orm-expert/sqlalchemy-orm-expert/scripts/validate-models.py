#!/usr/bin/env python3
"""
Validate SQLAlchemy model definitions.

Checks for common issues:
- Missing indexes on foreign keys
- Missing nullable constraints
- Timezone-naive DateTime columns
- Missing relationships or back_populates
- Improper use of Mapped types
"""

import sys
import inspect
from typing import get_type_hints
from sqlalchemy import Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, relationship

def validate_model(model_class):
    """Validate a single SQLAlchemy model class."""
    issues = []
    model_name = model_class.__name__
    
    # Check if using declarative base
    if not isinstance(model_class, type) or not issubclass(model_class, DeclarativeBase):
        issues.append(f"{model_name}: Not a valid DeclarativeBase model")
        return issues
    
    # Get mapped columns
    mapper = model_class.__mapper__
    
    # Check for foreign keys without indexes
    for col in mapper.columns:
        if col.foreign_keys:
            # Check if column has index
            if not col.index and not any(
                col.name in idx.columns for idx in model_class.__table__.indexes
            ):
                issues.append(
                    f"{model_name}.{col.name}: Foreign key without index (add index=True)"
                )
    
    # Check for DateTime columns without timezone
    for col in mapper.columns:
        if isinstance(col.type, DateTime):
            if not col.type.timezone:
                issues.append(
                    f"{model_name}.{col.name}: DateTime without timezone=True"
                )
    
    # Check for missing nullable constraints
    for col in mapper.columns:
        if col.name not in ['id'] and col.nullable is None:
            issues.append(
                f"{model_name}.{col.name}: Missing explicit nullable constraint"
            )
    
    # Check for relationships without back_populates
    for rel in mapper.relationships:
        if not rel.back_populates and not rel.backref:
            issues.append(
                f"{model_name}.{rel.key}: Relationship without back_populates"
            )
    
    # Check for proper Mapped type usage
    type_hints = get_type_hints(model_class)
    for attr_name, type_hint in type_hints.items():
        if attr_name.startswith('_'):
            continue
        
        # Check if it's a mapped attribute
        if hasattr(type_hint, '__origin__'):
            origin = type_hint.__origin__
            if origin is not Mapped:
                issues.append(
                    f"{model_name}.{attr_name}: Not using Mapped[] type (use Mapped[type])"
                )
    
    return issues

def validate_models(models):
    """Validate multiple models and report issues."""
    all_issues = []
    
    for model in models:
        issues = validate_model(model)
        all_issues.extend(issues)
    
    return all_issues

if __name__ == "__main__":
    print("SQLAlchemy Model Validator")
    print("=" * 50)
    
    # Example usage (replace with your models)
    print("\nTo use this script:")
    print("1. Import your models")
    print("2. Call validate_models([Model1, Model2, ...])")
    print("3. Fix reported issues")
    print("\nExample:")
    print("  from app.models import User, Ticket, Comment")
    print("  issues = validate_models([User, Ticket, Comment])")
    print("  for issue in issues:")
    print("      print(issue)")
    
    # Placeholder for actual validation
    # Replace with your model imports and validation call
    
    sys.exit(0)
