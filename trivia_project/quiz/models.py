from django.db import models


class Player(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Ensures each player name is unique
    total_score = models.IntegerField(default=0)  # Overall score across all rounds

    def __str__(self):
        return self.name


class RoundScore(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='round_scores')
    score = models.IntegerField()
    date_played = models.DateTimeField(auto_now_add=True)  # Timestamp when the round was played

    def __str__(self):
        return f'{self.player.name} - {self.score} on {self.date_played}'
