
// document.addEventListener('DOMContentLoaded', () => {
//     const questionContainer = document.getElementById('question-container');
//     const nextQuestionBtn = document.getElementById('next-question-btn');
//     let currentQuestionIndex = 0;
//     let score = 0;
//     let timer;
//
//     function startTimer() {
//         let timeLeft = 300; // 5 minutes
//         timer = setInterval(() => {
//             timeLeft--;
//             document.getElementById('timer').textContent = `Time Left: ${timeLeft}s`;
//             if (timeLeft <= 0) {
//                 clearInterval(timer);
//                 endGame();
//             }
//         }, 1000);
//     }
//
//     function loadQuestion() {
//         const questionData = JSON.parse('{{ questions|escapejs }}');
//         if (currentQuestionIndex < questionData.length) {
//             const question = questionData[currentQuestionIndex];
//             document.getElementById('question').textContent = question.question;
//             const optionsContainer = document.getElementById('options');
//             optionsContainer.innerHTML = ''; // Clear previous options
//
//             [...question.incorrect_answers, question.correct_answer].sort().forEach(option => {
//                 const button = document.createElement('button');
//                 button.className = 'option-btn';
//                 button.textContent = option;
//                 button.addEventListener('click', () => checkAnswer(option, question.correct_answer));
//                 optionsContainer.appendChild(button);
//             });
//         } else {
//             endGame();
//         }
//     }
//
//     function checkAnswer(selectedOption, correctOption) {
//         const feedback = document.getElementById('feedback');
//         if (selectedOption === correctOption) {
//             feedback.textContent = 'Correct! Well done!';
//             score += 10;
//             document.getElementById('score').textContent = `Score: ${score}`;
//         } else {
//             feedback.textContent = `Wrong answer. The correct answer was: ${correctOption}`;
//         }
//         currentQuestionIndex++;
//         setTimeout(loadQuestion, 2000); // Load next question after 2 seconds
//     }
//
//     function endGame() {
//         document.getElementById('game-over-container').style.display = 'block';
//         document.getElementById('question-container').style.display = 'none';
//         // Send the score to the server or save it as needed
//     }
//
//     startTimer();
//     loadQuestion();
//
//     nextQuestionBtn.addEventListener('click', () => loadQuestion());
// });

document.addEventListener('DOMContentLoaded', function() {
    fetchQuestions();
    document.getElementById('next-question-btn').addEventListener('click', function() {
        fetchQuestions();
    });
});

let questions = [];
let currentQuestionIndex = 0;
let score = 0;
let timerInterval;
const initialTime = 120; // 5 minutes
let timeLeft = initialTime;

function fetchQuestions() {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    fetch('/quiz/questions/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken
        }
    })
    .then(response => response.json())
    .then(data => {
        questions = data;
        showQuestion();
        startTimer();
    })
    .catch(error => console.error('Error fetching questions:', error));
}

function showQuestion() {
    if (currentQuestionIndex >= questions.length) {
        handleGameOver();  // Changed to handle game over directly
        return;
    }

    const question = questions[currentQuestionIndex];
    const options = [...question.incorrect_answers, question.correct_answer].sort();

    document.getElementById('question').textContent = question.question;
    const optionsContainer = document.getElementById('options');
    optionsContainer.innerHTML = '';

    options.forEach(option => {
        const button = document.createElement('button');
        button.textContent = option;
        button.classList.add('option-btn');
        button.addEventListener('click', function() {
            handleAnswer(option, question.correct_answer);
        });
        optionsContainer.appendChild(button);
    });

    document.getElementById('feedback').textContent = '';
    currentQuestionIndex++;
}

function handleAnswer(selectedAnswer, correctAnswer) {
    const feedback = document.getElementById('feedback');
    const isCorrect = selectedAnswer === correctAnswer;

    // Display feedback based on the answer
    if (isCorrect) {
        feedback.textContent = 'Correct! Amazing!';
        feedback.style.color = 'green';
        score += 10;  // Update local score
    } else {
        feedback.textContent = `Wrong! The correct answer is ${correctAnswer}.`;
        feedback.style.color = 'orange';
        
        feedback.classList.add('shake');

        setTimeout(() => {
            feedback.classList.remove('shake');
        }, 500);
    }
    document.getElementById('score').textContent = `Score: ${score}`;

    // Send answer to backend to update the session score
    fetch('/quiz/update-score/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name="csrfmiddlewaretoken"]').value
        },
        body: JSON.stringify({ answer: selectedAnswer })
    })
    .then(response => response.json())
    .then(data => {
        if (data.game_over) {
            handleGameOver(); // Game over logic
        } else {
            // Move to the next question after a delay to show feedback
            setTimeout(() => {
                showQuestion();
            }, 1500); // Wait for 1.5 seconds to show feedback
        }
    })
    .catch(error => console.error('Error updating score:', error));
}

function startTimer() {
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            handleGameOver();
            return;
        }
        timeLeft--;
        const minutes = Math.floor(timeLeft / 60);
        const seconds = timeLeft % 60;
        document.getElementById('timer').innerText = `Time Left: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
    }, 1000);
}

// function resetTimer() {
//     timeLeft = 300; // Reset to 5 minutes
//     startTimer(); // Restart timer
// }

function handleGameOver() {
    // Navigate to the game over page
    window.location.href = '/game-over/';
}



