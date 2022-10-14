from django.db import models


class Articles(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    date = models.DateTimeField()
    author = models.CharField(max_length=255)
    authorlink = models.CharField(max_length=255)
    postlink = models.CharField(max_length=255)
    hubs = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'articles'
        verbose_name = "Article"
        verbose_name_plural = "Articles"
        ordering = ["id"]
