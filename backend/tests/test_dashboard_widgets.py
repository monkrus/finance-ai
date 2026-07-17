import pytest
from app.dashboard.widgets import WidgetBuilder
from datetime import datetime

def test_widget_builder_auto_detect_positive():
    w = WidgetBuilder.build(title="Test", value=100.0, change=5.0)
    assert w.trend == "up"
    assert w.status == "success"
    assert w.title == "Test"
    assert w.value == 100.0

def test_widget_builder_auto_detect_negative():
    w = WidgetBuilder.build(title="Test", value=100.0, change=-5.0)
    assert w.trend == "down"
    assert w.status == "danger"

def test_widget_builder_auto_detect_flat():
    w = WidgetBuilder.build(title="Test", value=100.0, change=0.0)
    assert w.trend == "flat"
    assert w.status == "neutral"

def test_widget_builder_explicit_overrides():
    w = WidgetBuilder.build(title="Test", value=100.0, change=5.0, trend="down", status="warning")
    assert w.trend == "down"
    assert w.status == "warning"
