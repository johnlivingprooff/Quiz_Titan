import random
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Player, RoundScore
from pathlib import Path
import requests
import json

# Define a constant for the path to the fallback questions file
FALLBACK_QUESTIONS_PATH = Path(__file__).resolve().parent / 'data' / 'fallback_questions.json'


def load_fallback_questions():
    """Load fallback questions from a local JSON file."""
    with open(FALLBACK_QUESTIONS_PATH, 'r') as file:
        questions = json.load(file)
    return questions


def index(request):
    if request.method == 'POST':
        player_name = request.POST.get('player_name')
        # Check if player exists; if not, create one
        player, created = Player.objects.get_or_create(name=player_name)
        request.session['player_id'] = player.id  # Store player ID in session
        return redirect('select_options')
    return render(request, 'quiz/index.html')


def select_options(request):
    if request.method == 'POST':
        genre = request.POST.get('genre')
        difficulty = request.POST.get('difficulty')
        request.session['genre'] = genre
        request.session['difficulty'] = difficulty
        return redirect('quiz')
    return render(request, 'quiz/select_options.html')


# def quiz(request):
#     # Fetch questions from Open Trivia Database API
#     player_name = request.session.get('player_name', 'Guest')
#     genre = request.session.get('genre', '9')
#     difficulty = request.session.get('difficulty', 'easy')
#     url = f'https://opentdb.com/api.php?amount=10&category={genre}&difficulty={difficulty}&type=multiple'
#     response = requests.get(url)
#     questions = response.json().get('results', [])
#
#     if not questions:
#         return redirect('game_over')
#
#     request.session['questions'] = questions
#     request.session['current_question'] = 0
#     request.session['score'] = 0
#
#     context = {
#         'player_name': player_name,
#         'questions': questions,
#         'current_question': 0,
#         'score': 0
#     }
#
#     return render(request, 'quiz/quiz.html', context)


def quiz(request):
    # Fetch questions from Open Trivia Database API
    player_name = request.session.get('player_name', 'Guest')
    genre = request.session.get('genre', '9')
    difficulty = request.session.get('difficulty', 'easy')
    url = f'https://opentdb.com/api.php?amount=10&category={genre}&difficulty={difficulty}&type=multiple'

    try:
        response = requests.get(url)
        response.raise_for_status()
        questions = response.json().get('results', [])
        if not questions:
            raise ValueError("No questions fetched from OpenTDB.")
    except (requests.RequestException, ValueError):
        # If OpenTDB fails or returns no questions, load fallback questions
        questions = load_fallback_questions()

    # If no questions are available (even fallback), handle gracefully
    if not questions:
        return redirect('game_over')

    request.session['questions'] = questions
    request.session['current_question'] = 0
    request.session['score'] = 0

    context = {
        'player_name': player_name,
        'questions': questions,
        'current_question': 0,
        'score': 0
    }

    return render(request, 'quiz/quiz.html', context)


def get_questions(request):
    questions = request.session.get('questions', [])
    if not questions:
        return JsonResponse({'error': 'No questions available'}, status=404)
    return JsonResponse(questions, safe=False)


def update_score(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        answer = data.get('answer')
        current_question = request.session.get('current_question', 0)
        questions = request.session.get('questions', [])
        player_id = request.session.get('player_id')

        if not questions or current_question >= len(questions):
            return JsonResponse({'error': 'Invalid state'}, status=400)

        correct_answer = questions[current_question]['correct_answer']
        score = request.session.get('score', 0)

        if answer == correct_answer:
            score += 10  # Increase score by 10 for correct answer
            request.session['score'] = score

        # Move to the next question
        request.session['current_question'] += 1

        if player_id:
            player = Player.objects.get(id=player_id)
            # Update or create a new RoundScore for this session
            RoundScore.objects.update_or_create(
                player=player,
                date_played=request.session.get('game_start_time'),
                defaults={'score': score}
            )

        if request.session['current_question'] >= len(questions):
            # If the game is over, return game over status
            return JsonResponse({'game_over': True, 'score': score})

        # Prepare the next question
        next_question = questions[request.session['current_question']]
        options = next_question['incorrect_answers'] + [next_question['correct_answer']]
        random.shuffle(options)

        return JsonResponse({
            'next_question': True,
            'question': next_question['question'],
            'options': '<br>'.join(
                [f'<button class="option-btn" data-answer="{opt}">{opt}</button>' for opt in options]),
            'score': score  # Include the updated score in the response
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)


def game_over(request):
    score = request.session.get('score', 0)
    player_id = request.session.get('player_id')

    if player_id:
        player = Player.objects.get(id=player_id)
        # Calculate new overall score
        player.total_score += score
        player.save()

        # Record the round score in RoundScore model
        RoundScore.objects.create(player=player, score=score)

    return render(request, 'quiz/game_over.html', {'score': score, 'overall_score': player.total_score})
