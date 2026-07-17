import pytest
from app.ai.prompt_manager import PromptManager
from app.ai.models import PromptTemplate
from app.core.exceptions import FinPilotException

def test_prompt_manager_registration():
    pm = PromptManager()
    
    t = PromptTemplate(name="test_prompt", template="Hello {name}", version="1.0.0")
    pm.register(t)
    
    assert pm.get_template("test_prompt") == "Hello {name}"
    assert pm.get_template("test_prompt", "1.0.0") == "Hello {name}"
    
    with pytest.raises(FinPilotException) as exc:
        pm.get_template("missing")
    assert exc.value.status_code == 404

def test_prompt_manager_render():
    pm = PromptManager()
    
    t = PromptTemplate(name="greet", template="Hi {user}")
    pm.register(t)
    
    res = pm.render("greet", user="Alice")
    assert res == "Hi Alice"
    
    with pytest.raises(FinPilotException) as exc:
        pm.render("greet", wrong="Bob")
    assert exc.value.status_code == 400
