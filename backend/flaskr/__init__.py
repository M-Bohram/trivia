import os, sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resources={r"*": {'origins': "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Authorization, Content-Type')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories')
  def get_categories():
      categories = Category.query.all()
      formatted_categories = { category.format()['id']: category.format()['type'] for category in categories }
      return jsonify({ "categories": formatted_categories, "total_categories": len(formatted_categories)})


  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions')
  def get_paginated_questions():
      page_num = int(request.args.get('page', 1))
      start = QUESTIONS_PER_PAGE * (page_num -1)
      end = page_num * QUESTIONS_PER_PAGE
      total_questions = Question.query.order_by('id').all()
      questions = total_questions[start:end]
      if questions:
        formatted_questions = [ question.format() for question in questions ]
        categories = Category.query.all()
        formatted_categories = { category.format()['id']: category.format()['type'] for category in categories }
        return jsonify({ "questions": formatted_questions, "total_questions": len(total_questions), "categories": formatted_categories})
      else:
        abort(404)

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''

  @app.route('/questions/<int:questionId>', methods=['DELETE'])
  def delete_question(questionId):
      question = Question.query.get(questionId)
      if question is None:
        abort(422)
      question.delete()
      return jsonify({ "delete": True, "id": questionId})


  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''

  @app.route('/questions', methods=['POST'])
  def create_question():
    if request.get_json() and 'searchTerm' in request.get_json():
      search_term = request.get_json()['searchTerm']
      questions = Question.query.order_by('id').filter(Question.question.ilike('%{}%'.format(search_term))).all()
      if not questions:
        abort(404)
      formatted_questions = [ question.format() for question in questions ]
      total_questions = len(formatted_questions)
      return jsonify({ "questions": formatted_questions, "total_questions": total_questions})
    else:
      if request.get_json() and 'question' in request.get_json() and 'answer' in request.get_json() and 'category' in request.get_json() and 'difficulty' in request.get_json():
        question_text = request.get_json()['question']
        answer_text = request.get_json()['answer']
        category = request.get_json()['category']
        difficulty_score = request.get_json()['difficulty']
        print(request.get_json())
        question = Question(question=question_text, answer=answer_text, category=category, difficulty=difficulty_score)
        question.insert()
        return jsonify({ "created": "true"})
      else:
        abort(400)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''

  # implemented above with creating new question

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:categoryId>/questions')
  def get_questions_from_category(categoryId):
    category = Category.query.filter(Category.id==categoryId).one_or_none()
    if category is None:
      abort(404)
    current_category = Category.query.get(categoryId).format()['type']
    questions = Question.query.filter_by(category=categoryId).all()
    if not questions:
      abort(404)
    formatted_questions = [ question.format() for question in questions ]
    total_questions = len(formatted_questions)
    return jsonify({ "questions": formatted_questions, "total_questions": total_questions, "current_category": current_category})



  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''

  @app.route('/quizzes', methods=['POST'])
  def start_quiz():
    if request.get_json() and 'previous_questions' in request.get_json() and 'quiz_category' in request.get_json():
      previous_questions = request.get_json()['previous_questions']
      quiz_category_id = request.get_json()['quiz_category']
      if quiz_category_id == 0:  # if he selected ALL category
        categories = Category.query.all()
        formatted_categories = [ category.format() for category in categories ]
        category_ids = [ category['id'] for category in formatted_categories ]
        random_category_ids = [ random.randint(category_ids[0], len(category_ids) - 1) for _ in range(3)]
        category_ids_no_duplicates = list(dict.fromkeys(random_category_ids))
        all_questions_of_category_list_of_lists = [Question.query.filter_by(category=str(id)).all() for id in category_ids_no_duplicates]
        all_questions_of_category_one_list = []
        for _list in all_questions_of_category_list_of_lists:
          for _item in _list:
            all_questions_of_category_one_list.append(_item)
        all_questions_of_category = all_questions_of_category_one_list[:5]
      else:
        all_questions_of_category = Question.query.filter_by(category=quiz_category_id).all()
      if not all_questions_of_category:
        abort(404)
      formatted_all_questions = [ question.format() for question in all_questions_of_category ]
      filtered_questions = [ question for question in formatted_all_questions if question['id'] not in previous_questions ]
      if filtered_questions:
        json_res = { "question": filtered_questions[0]} 
      else:
        json_res = { "end": True }
      return jsonify(json_res)
    else:
      abort(400)


  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''

  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      "success": False,
      "status_code": 400,
      "message": "bad request"
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "status_code": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      "success": False,
      "status_code": 405,
      "message": "method not allowed"
    }), 405

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "status_code": 422,
      "message": "unprocessable"
    }), 422

  @app.errorhandler(500)
  def unprocessed(error):
    return jsonify({
      "success": False,
      "status_code": 500,
      "message": "unprocessed"
    }), 500

  
  return app

    