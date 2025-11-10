# Contributing to Brand Forge

## Progress Tracking for AI Agents

This project uses **GitHub Issues with Hierarchical Sub-Issues + GitHub Projects** for progress tracking. All progress is accessible locally via `gh` CLI.

### Issue Hierarchy

```
Milestone (timeboxed release/sprint group)
  ↓
Epic (parent issue - large feature/initiative)
  ↓
Feature (sub-issue L1 - user-facing functionality)
  ↓
Task (sub-issue L2+ - implementation work)
```

**Key Features**:
- **Sub-issues**: Each feature/task is a full GitHub issue (not just a checklist)
- **Automatic progress**: When you close a sub-issue, progress rolls up to the parent epic automatically
- **Up to 8 levels**: Deep hierarchy support for complex projects
- **Milestones**: Group related epics by timeline/release

---

## Quick Reference

### View Current Progress

```bash
# View all issues (epics, features, tasks)
gh issue list --repo IAMSamuelRodda/brand-forge

# View all epics
gh issue list --search "label:type:epic" --repo IAMSamuelRodda/brand-forge

# View specific epic with sub-issues
gh issue view 1 --repo IAMSamuelRodda/brand-forge

# View project board in browser
gh project view 6 --owner IAMSamuelRodda --web

# View roadmap (timeline visualization)
gh project view 6 --owner IAMSamuelRodda --web
# Switch to "Roadmap" view in UI
```

### View Work by Status

```bash
# All pending work
gh issue list --state open --label "status: pending" --repo IAMSamuelRodda/brand-forge

# In-progress work
gh issue list --state open --label "status: in-progress" --repo IAMSamuelRodda/brand-forge

# Blocked work
gh issue list --state open --label "status: blocked" --repo IAMSamuelRodda/brand-forge

# View work by milestone
gh issue list --milestone "v1.0 Foundation & Core Pipeline" --repo IAMSamuelRodda/brand-forge
```

---

## Updating Progress

### Starting Work on an Epic

```bash
# Mark epic as in-progress
gh issue edit 1 \
  --remove-label "status: pending" \
  --add-label "status: in-progress" \
  --repo IAMSamuelRodda/brand-forge

# Add start comment
gh issue comment 1 --body "Started epic: Project Foundation & Infrastructure" --repo IAMSamuelRodda/brand-forge
```

### Working on Features/Tasks (Sub-Issues)

```bash
# Start a feature/task
gh issue edit 2 \
  --remove-label "status: pending" \
  --add-label "status: in-progress" \
  --repo IAMSamuelRodda/brand-forge

# ... do the work ...

# Complete the feature/task (progress rolls up to parent epic automatically!)
gh issue close 2 --comment "Feature complete: Project Structure & Environment Setup" --repo IAMSamuelRodda/brand-forge
gh issue edit 2 --add-label "status: completed" --repo IAMSamuelRodda/brand-forge

# Verify parent epic shows updated progress
gh issue view 1 --repo IAMSamuelRodda/brand-forge
```

### Marking Work as Blocked (with Dependency Link)

```bash
# Add blocked label and comment with link to blocking issue
gh issue edit 17 --add-label "status: blocked" --repo IAMSamuelRodda/brand-forge
gh issue comment 17 --body "Blocked by #9: Waiting for model configuration setup" --repo IAMSamuelRodda/brand-forge

# When unblocked, update status
gh issue edit 17 --remove-label "status: blocked" --add-label "status: in-progress" --repo IAMSamuelRodda/brand-forge
gh issue comment 17 --body "Unblocked: Configuration complete, resuming research" --repo IAMSamuelRodda/brand-forge
```

### Completing an Epic

```bash
# When all sub-issues are complete, close the epic
gh issue close 1 --comment "Epic complete: All infrastructure and configuration features delivered" --repo IAMSamuelRodda/brand-forge
gh issue edit 1 --add-label "status: completed" --repo IAMSamuelRodda/brand-forge
```

---

## Best Practices for Agents

### 1. Check Current Progress Before Starting

```bash
# Always check what's already done
gh issue list --state open --repo IAMSamuelRodda/brand-forge

# Check epic hierarchy
gh issue view 1 --repo IAMSamuelRodda/brand-forge

# View milestone progress
gh issue list --milestone "v1.0 Foundation & Core Pipeline" --repo IAMSamuelRodda/brand-forge
```

### 2. Update Status When Starting Work

```bash
# Mark epic/feature/task as in-progress when you start
gh issue edit 2 \
  --remove-label "status: pending" \
  --add-label "status: in-progress" \
  --repo IAMSamuelRodda/brand-forge
```

### 3. Comment on Progress

```bash
# Add progress comments to epics
gh issue comment 1 --body "Completed feature #2: Project Structure & Environment Setup" --repo IAMSamuelRodda/brand-forge

# Add progress comments to features/tasks
gh issue comment 2 --body "Implemented virtual environment with uv package manager and directory structure" --repo IAMSamuelRodda/brand-forge
```

### 4. Close Sub-Issues (Progress Rolls Up Automatically)

```bash
# When a feature/task is complete, close it
gh issue close 2 --comment "Feature complete" --repo IAMSamuelRodda/brand-forge
gh issue edit 2 --add-label "status: completed" --repo IAMSamuelRodda/brand-forge

# Parent epic automatically shows updated progress!
# No manual checkbox updates needed
```

### 5. Link Related Commits

```bash
# Reference feature/task issue in commit messages
git commit -m "feat: implement prompt generation engine

- Built template processor for PROMPT-TEMPLATES-*.md files
- Variable substitution for brand palette and visual direction
- Model-specific formatting (SD vs DALL-E vs Flux)

Relates to #12 (Epic #11)

🤖 Generated with [Claude Code](https://claude.com/claude-code)"
```

### 6. Update Blueprint if Requirements Change

If requirements change during implementation:

1. Document change in issue comment
2. Update `specs/BLUEPRINT.yaml` if needed
3. Create follow-up issue if scope changes significantly

```bash
# Document requirements change
gh issue comment 17 --body "Requirements update: Switching from self-hosted to Stability AI API

Original: Research and deploy self-hosted Stable Diffusion
Updated: Use Stability AI API ($0.004/image)
Reason: Faster iteration, lower complexity for MVP, cost-effective at current scale" --repo IAMSamuelRodda/brand-forge
```

---

## Epic-Milestone Mapping

| Epic # | Epic Name | Timeline | Milestone | Features |
|--------|-----------|----------|-----------|----------|
| #1 | Project Foundation & Infrastructure | Week 1 | v1.0 Foundation & Core Pipeline | #2, #5, #8 |
| #11 | Basic Generation Pipeline (Single Model) | Weeks 1-2 | v1.0 Foundation & Core Pipeline | #12, #16, #20 |
| #24 | Quality Scoring & Filtering System | Weeks 2-3 | v1.0 Foundation & Core Pipeline | #25, #30, #33, #36 |
| #39 | Human Approval Interface | Week 3 | v1.0 Foundation & Core Pipeline | #40, #43, #47 |
| #50 | Multi-Model Generation Pipeline | Weeks 5-6 | v1.1 Multi-Model & Iterative Refinement | #51, #54, #57, #61 |
| #64 | Iterative Refinement Pipeline | Weeks 6-7 | v1.1 Multi-Model & Iterative Refinement | #65, #69, #72 |
| #75 | Production Finalization & Export | Weeks 7-8 | v1.1 Multi-Model & Iterative Refinement | #76, #80, #83, #87 |
| #91 | Testing & Quality Assurance | Week 9 | v1.2 Production Polish & Documentation | #92, #96, #99 |
| #102 | Performance Optimization | Weeks 9-10 | v1.2 Production Polish & Documentation | #103, #106, #109 |
| #112 | Documentation & User Experience | Week 10 | v1.2 Production Polish & Documentation | #113, #117, #120, #123 |

**Note**: Each epic contains multiple feature sub-issues, which may contain task sub-issues (up to 8 levels deep).

---

## Project Links

- **GitHub Repository**: https://github.com/IAMSamuelRodda/brand-forge
- **Project Board**: https://github.com/users/IAMSamuelRodda/projects/6
- **Issues**: https://github.com/IAMSamuelRodda/brand-forge/issues
- **Blueprint**: `/home/samuel/repos/brand-forge/specs/BLUEPRINT.yaml`

---

## Troubleshooting

### gh CLI Not Authenticated

```bash
gh auth status
gh auth refresh -h github.com -s project,read:project
```

### Can't Create Sub-Issues via gh CLI

gh CLI doesn't have native sub-issue commands yet. Use:
```bash
# Open epic in browser
gh issue view 1 --web --repo IAMSamuelRodda/brand-forge
# Click "Create sub-issue" button at bottom of description
```

Or use GraphQL API (see skill documentation).

### Sub-Issue Progress Not Showing

Progress rolls up automatically when you close sub-issues:
```bash
# Close the sub-issue
gh issue close 2 --repo IAMSamuelRodda/brand-forge

# View parent epic to see updated progress
gh issue view 1 --repo IAMSamuelRodda/brand-forge
```

### Need to See Detailed BLUEPRINT

```bash
cat /home/samuel/repos/brand-forge/specs/BLUEPRINT.yaml | less
# Or open in editor
code /home/samuel/repos/brand-forge/specs/BLUEPRINT.yaml
```

### View Roadmap Timeline

```bash
# Open project roadmap view in browser
gh project view 6 --owner IAMSamuelRodda --web
# Switch to "Roadmap" view in UI for timeline visualization
```

---

## Example Workflow

```bash
# 1. Check current state
gh issue list --state open --repo IAMSamuelRodda/brand-forge

# 2. View epic hierarchy
gh issue view 1 --repo IAMSamuelRodda/brand-forge  # Epic #1: Project Foundation

# 3. Start working on Epic #1
gh issue edit 1 \
  --remove-label "status: pending" \
  --add-label "status: in-progress" \
  --repo IAMSamuelRodda/brand-forge
gh issue comment 1 --body "Started epic: Project Foundation & Infrastructure" --repo IAMSamuelRodda/brand-forge

# 4. Work on Feature #2 (sub-issue of Epic #1)
gh issue edit 2 \
  --remove-label "status: pending" \
  --add-label "status: in-progress" \
  --repo IAMSamuelRodda/brand-forge

# 5. Do the implementation work...
cd /home/samuel/repos/brand-forge
mkdir -p automation/{config,src,web,results,data}
python3 -m venv automation/.venv
source automation/.venv/bin/activate
# ... create requirements.txt, etc ...

# 6. Commit with issue reference
git add .
git commit -m "feat: initialize Python environment and directory structure

- Created automation directory with subdirectories (config, src, web, results, data)
- Set up Python 3.11 virtual environment with venv
- Created .gitignore for results/ and data/
- Added README placeholders

Relates to #2 → #1 (Project Foundation & Infrastructure)

🤖 Generated with [Claude Code](https://claude.com/claude-code)"

# 7. Complete Feature #2
gh issue close 2 --comment "Feature complete: Project structure created, virtual environment configured" --repo IAMSamuelRodda/brand-forge
gh issue edit 2 --add-label "status: completed" --repo IAMSamuelRodda/brand-forge

# 8. Verify epic shows updated progress (automatic!)
gh issue view 1 --repo IAMSamuelRodda/brand-forge
# Epic #1 now shows Feature #2 as completed

# 9. Continue with next feature (#5: Design Asset Integration, #8: Configuration Management)...

# 10. When all features complete, close epic
gh issue close 1 --comment "Epic complete: Project foundation established with Python environment, design asset integration, and configuration system" --repo IAMSamuelRodda/brand-forge
gh issue edit 1 --add-label "status: completed" --repo IAMSamuelRodda/brand-forge
```

---

## Agent Coordination

When multiple agents work on the project:

1. **Check issue status first**: View epic hierarchy and sub-issue status
2. **Avoid duplicate work**: Check labels and comments on epics and features
3. **Communicate**: Add comments when starting/finishing features/tasks
4. **Use branches**: Create feature branches for parallel work on different epics/features

```bash
# Check who's working on what
gh issue list --state open --label "status: in-progress" --repo IAMSamuelRodda/brand-forge

# View epic to see which features are in progress
gh issue view 11 --repo IAMSamuelRodda/brand-forge

# Check blocked work
gh issue list --label "status: blocked" --repo IAMSamuelRodda/brand-forge
```

### Parallel Work Strategy

Multiple agents can work on different features within the same epic:
- **Agent 1**: Works on Feature #12 (Prompt Generation Engine)
- **Agent 2**: Works on Feature #16 (Stable Diffusion API Integration)
- Both are sub-issues of Epic #11 (Basic Generation Pipeline)
- Progress rolls up to Epic #11 automatically as features complete

---

## Need Help?

- Review `specs/BLUEPRINT.yaml` for detailed technical specifications
- Check git history: `git log --oneline`
- View all issues: `gh issue list --state all --repo IAMSamuelRodda/brand-forge`
- Open project board: `gh project view 6 --owner IAMSamuelRodda --web`
