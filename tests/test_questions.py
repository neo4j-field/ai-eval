import os
import json
import tempfile
import pytest
from src.questions import Questions, Question

SAMPLE_JSON = {
    "questions": [
        {
            "id": "q1",
            "question": "What is the capital of France?",
            "ground_truth": "Paris"
        },
        {
            "id": "q2",
            "question": "What is 2 + 2?",
            "ground_truth": "4"
        }
    ]
}

def test_load_from_json():
    # Create a temporary JSON file
    with tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".json") as tmpfile:
        json.dump(SAMPLE_JSON, tmpfile)
        tmpfile_path = tmpfile.name

    try:
        questions = Questions.load_from_json(tmpfile_path)
        assert isinstance(questions, Questions)
        # Check that both questions are loaded
        q1 = questions.get_question_by_id("q1")
        q2 = questions.get_question_by_id("q2")
        assert isinstance(q1, Question)
        assert isinstance(q2, Question)
        assert q1.question == "What is the capital of France?"
        assert q1.ground_truth == "Paris"
        assert q2.question == "What is 2 + 2?"
        assert q2.ground_truth == "4"
    finally:
        os.remove(tmpfile_path)

def test_iterate_questions():
    questions = Questions()
    q1 = Question("id1", "What is Python?", "A programming language")
    q2 = Question("id2", "What is 2+2?", "4")
    questions.add_question(q1)
    questions.add_question(q2)
    questions_dict = questions.get_questions()
    texts = []
    for question in questions_dict.values():
        texts.append(question.question)
    assert "What is Python?" in texts
    assert "What is 2+2?" in texts
    assert len(texts) == 2