import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def pagination(request, getlist):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE
    questions = [question.format() for question in getlist]
    result_of_question = questions[start:end]
    return result_of_question

def create_app(test_config=None):
  # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    cors = CORS(app)
    
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        return response
    
    @app.route('/categories')
    def get_categories():
      categories_all = Category.query.all()
      formatted_categories = {
        category.id: category.type for category in categories_all}
      
      return jsonify({
          'success':True,
          'categories':formatted_categories
      })
      
    @app.route('/questions')
    def get_questions():
      categories_all = Category.query.all()
      questions_all = Question.query.all()
      formatted_questions = [question.format() for question in questions_all]
      formatted_categories = {
        category.id: category.type for category in categories_all}
      questions_list = pagination(request, questions_all)
      
      if not len(questions_list):
        abort(404)
      
      return jsonify({
          'success':True,
          'categories':formatted_categories,
          'total_questions':len(formatted_questions),
          'questions':questions_list
          
      })
      
    @app.route('/categories/<int:category_id>/questions')
    def get_categories_id_question(category_id):
      try:
          this_question = Question.query.filter(Question.category == category_id).all()
          if not this_question:
            abort(404)
          categories_all = Category.query.all()
          formatted_questions = [question.format() for question in this_question]
          formatted_categories = {
            category.id: category.type for category in categories_all}
          questions_list = pagination(request, this_question)

          
          return jsonify({
              'success':True,
              'categories':formatted_categories,
              'total_questions':len(formatted_questions),
              'questions':questions_list,
              'current_category': category_id  
          })
      except BaseException:
            abort(500)
            
    @app.route('/questions', methods=['POST'])
    def create_question():
      body = request.get_json()
      
      new_question = body.get('question', None)
      new_answer = body.get('answer', None)
      new_category = body.get('category', None)
      new_difficulty = body.get('difficulty', None)
      
      try:
        question = Question(question=new_question, answer=new_answer, 
                            category=new_category, difficulty=new_difficulty)
        question.insert()
        
        selection = Question.query.order_by(Question.id).all()
        current_questions = pagination(request, selection)
        
        return jsonify({
              'success':True,
              })
        
      except:
        abort(405)
        
    
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
      try:
        search_term = request.json.get('searchTerm')
        get_search_question = Question.query.filter(
          Question.question.ilike(f'%{search_term}%')).all()
        if not get_search_question:
          abort(404)
        formatted_search = [question.format() for question in get_search_question]
        question_pagination = pagination(request, get_search_question)
        category_list = Category.query.all()
        category_types = {category.id: category.type for category in category_list}
        return jsonify({
          'success': True,
          'questions': question_pagination,
          'total_questions': len(formatted_search),
          'categories': category_types
        })
      except BaseException:
        abort(405)
    
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_questions():
      body = request.get_json()
      previous_questions =body.get('previous_questions', [])
      quiz_category = body.get('quiz_category', None)
      try:
        if quiz_category['type'] == 'click':
          quiz = Question.query.all()
        else:
          quiz = Question.query.filter_by(category=quiz_category['id']).all()
        if not quiz:
          return abort(422)
        selected = []
        for question in quiz:
          if question.id not in previous_questions:
            selected.append(question.format())
        if len(selected) != 0:
          result = random.choice(selected)
          return jsonify({
            'success': True,
            'question':result
          })
      except:
        abort(422)
        
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
      try:
        deleted = Question.query.get(question_id)
        if not deleted:
          abort(404)
        deleted.delete()
        return jsonify({
          'success':True
        })
      except BaseException:
        '''import traceback
        traceback.print_exc()'''
        abort(422)
        
        
    @app.errorhandler(500)
    def server_error(error):
      return jsonify({
        'error': 500,
        'message': 'The page you are looking for cannot be displayed due to a server problem.'
      }), 500
    
    @app.errorhandler(404)
    def not_found(error):
      return jsonify({
        'success': False,
        'error': 404,
        'message': 'The page you are looking for cannot be found.'
      }), 404
      
    @app.errorhandler(422)
    def not_processed(error):
      return jsonify({
        'error': 422,
        'message': 'Request cannot be processed'
      }), 422
      
    @app.errorhandler(400)
    def bad_request(error):
      return jsonify({
          "error": 400,
          "message": "The request cannot be fulfilled due to bad syntax."
      }), 400

    @app.errorhandler(405)
    def method_not_request(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "A request was made of a resource using a request method not supported by that resource."
      }), 405
    return app