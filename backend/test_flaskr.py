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
        self.database_path = "postgres:///{}".format(self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
        
        self.question = {
            'question': 'test question',
            'answer': 'test answer',
            'category': 1,
            'difficulty': 2
        }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories_successfully(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_categories'])


    def test_get_paginated_questions_successfully(self):
        res = self.client().get('/questions?page=1')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(len(data['questions']) == 10)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])


    def test_fail_getting_paginated_questions(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['status_code'], 404)
        self.assertEqual(data['message'], 'resource not found')


    def test_delete_question_successfully(self):
        res = self.client().delete('/questions/10')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['delete'], True)


    def test_fail_deleting_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['status_code'], 422)
        self.assertEqual(data['message'], 'unprocessable')


    def test_search_for_question_successfully(self):
        res = self.client().post('/questions', json={'searchTerm': 'body'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])


    def test_searching_for_not_exist_question(self):
        res = self.client().post('/questions', json={'searchTerm': 'weirdword'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['status_code'], 404)
        self.assertEqual(data['message'], 'resource not found')

        
    def test_create_question_successfully(self):
        res = self.client().post('/questions', json=self.question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['created'])


    def test_fail_creating_question(self):
        res = self.client().post('/questions/5', json=self.question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['status_code'], 405)
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_questions_from_categories_successfully(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])


    def test_fail_getting_questions_from_categories_category_or_questions_not_found(self):
        res = self.client().get('/categories/10/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['status_code'], 404)
        self.assertEqual(data['message'], 'resource not found')

    def test_start_quiz_successfully(self):
        req_body = {
            'previous_questions': [2,4,6],
            'quiz_category': 1
        }
        res = self.client().post('/quizzes', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['question'])


    def test_fail_starting_quiz_bad_request(self):
        req_body = {
            'previous_questions': [1,2,3,4]
        }
        res = self.client().post('/quizzes', json=req_body)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['status_code'], 400)
        self.assertEqual(data['message'], 'bad request')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()