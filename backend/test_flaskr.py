import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)
        self.new_question ={
            "question": 'Is this using python?',
            "answer": 'Yes',
            "category": 1,
            "difficulty": 1,
        }
        self.test_quiz ={
            "previous_questions": [1],
            "quiz_category": {"type": "Science", "id": 1}
        }
        self.test_quiz_error ={
            "previous_questions": [100],
            "quiz_category": {"type": "Python", "id": 100}
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
    
    def test_get_categories_404(self):
        res = self.client().get('/categories/3')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The page you are looking for cannot be found.')
        
    def test_get_questions(self):
        res = self.client().get('/questions?page=2')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        
    def test_get_questions_404(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The page you are looking for cannot be found.')
        
        
    def test_get_questions_by_categories(self):
        res = self.client().get('categories/3/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['current_category'], 3)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        
    def test_get_questions_by_categories_404(self):
        res = self.client().get('categories/get/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'The page you are looking for cannot be found.')
        
        
    def test_post_questions(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        
    def test_post_questions_405(self):
        res = self.client().post('/questions/1000', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'A request was made of a resource using a request method not supported by that resource.')
        
        
    def test_search_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'what'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        
    def test_search_questions_404(self):
        res = self.client().post('/questions/search', json={'search': 'python'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'A request was made of a resource using a request method not supported by that resource.')
        
    def test_post_quiz(self):
        res = self.client().post('/quizzes', json=self.test_quiz)  
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        
    def test_post_quiz_422(self):
        res = self.client().post('/quizzes', json=self.test_quiz_error)  
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Request cannot be processed')
        
    
    def test_delete_question(self):
        res = self.client().delete('/questions/22')
        data = json.loads(res.data)
        question = Question.query.filter(Question.id == 22).one_or_none()
        self.assertEqual(res.status_code, 200)
        #self.assertEqual(data['success'], False)
        self.assertEqual(question, None)
        
    def test_delete_question_422(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['message'], 'Request cannot be processed')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()