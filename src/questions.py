import json

class Question:
    def __init__(self, id, question, ground_truth):
        self._id = id
        self._question = question
        self._ground_truth = ground_truth

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def question(self):
        return self._question

    @question.setter
    def question(self, value):
        self._question = value

    @property
    def ground_truth(self):
        return self._ground_truth

    @ground_truth.setter
    def ground_truth(self, value):
        self._ground_truth = value


class Questions:
    def __init__(self):
        self._questions = {}

    def add_question(self, question):
        if question.id in self._questions:
            raise ValueError(f"Question with id '{question.id}' already exists.")
        self._questions[question.id] = question

    def remove_question_by_id(self, question_id):
        if question_id in self._questions:
            del self._questions[question_id]
        else:
            raise KeyError(f"No question found with id '{question_id}'.")

    def get_question_by_id(self, question_id):
        return self._questions.get(question_id)

    def get_questions(self):
        # Return a shallow copy to prevent external modification
        return self._questions.copy()
        
    @staticmethod
    def load_from_json(json_filename):
        with open(json_filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        questions = Questions()
        for q in data.get("questions", []):
            question = Question(
                id=q["id"],
                question=q["question"],
                ground_truth=q["ground_truth"],
            )
            questions.add_question(question)
        return questions

    def dump_to_json(self, json_filename):
        data = {"questions": [vars(q) for q in self._questions.values()]}
        with open(json_filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)