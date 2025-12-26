from celery import shared_task

@shared_task(bind=True, max_retries=5)
def process_subtask(self, subtask_id, idempotency_key=None):
    try:
        # processing logic placeholder
        return {"subtask_id": subtask_id, "status":"done"}
    except Exception as exc:
        countdown = min(60 * (2 ** self.request.retries), 3600)
        raise self.retry(exc=exc, countdown=countdown)
