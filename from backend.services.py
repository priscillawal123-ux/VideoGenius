from backend.services.checkpoint import save_progress_checkpoint


async def process_video_generation(
    job_id: str,
    request: VideoGenerationRequest,
    user_id: str,
    script_service: ScriptGeneratorService,
    db_client: BigQueryClient,
) -> None:
    """Background task to process video generation."""
    try:
        await db_client.update_job_status(job_id, "generating_script")

        # Generate script
        script_data = await script_service.generate_script(
            topic=request.topic,
            duration_seconds=request.duration_seconds,
            style=request.style.value,
            additional_context=request.additional_context,
        )

        # Save partial script and create 30% checkpoint
        checkpoint_snapshot = {
            "title": script_data.get("title"),
            "hook": script_data.get("hook"),
            "script_preview": "\n".join(
                script_data.get("script", "").splitlines()[:10]
            ),
            "estimated_timestamps": {"hook_end": 5, "first_section_end": 30},
        }

        # Persist checkpoint (30%)
        await save_progress_checkpoint(job_id, db_client, 30, checkpoint_snapshot)

        # Update with full script
        await db_client.update_job_data(job_id, {"script": script_data})

        # Continue with other steps...
        await db_client.update_job_status(job_id, "completed")
        logger.info("Video generation completed: %s", job_id)

    except Exception as e:
        logger.error("Video generation failed for %s: %s", job_id, e)
        await db_client.update_job_status(job_id, "failed", error=str(e))
