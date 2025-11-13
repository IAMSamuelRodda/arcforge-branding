# Results Directory

This directory stores generated images organized by session and stage.

## Structure

```
results/
├── {session_id}/
│   ├── stage_1_concept/
│   │   └── {image_id}.png
│   ├── stage_2_refinement/
│   │   └── {image_id}.png
│   └── stage_3_production/
│       └── {image_id}.png
```

## Retention Policy

- Generated images are retained for 30 days
- Approved images are moved to permanent storage in `assets/`
- Automatic cleanup runs weekly to remove old sessions

## Gitignore

This directory is gitignored to prevent large binary files from being committed to the repository.
