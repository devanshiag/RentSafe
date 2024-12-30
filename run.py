from app import create_app
from app.tasks import scheduler

app = create_app()

if __name__ == "__main__":
    if not scheduler.running:
        scheduler.start()
        app.logger.info("Scheduler started successfully.")
    app.run(debug=True, use_reloader=False)
