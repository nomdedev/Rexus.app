"""Módulo de Compras"""
from .view_complete import ComprasViewComplete as ComprasView
from rexus.utils.unified_sanitizer import unified_sanitizer, sanitize_string, sanitize_numeric

__all__ = ['ComprasView']
