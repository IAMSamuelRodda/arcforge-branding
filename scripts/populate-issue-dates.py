#!/usr/bin/env python3
"""
Populate GitHub Project date fields for existing issues using AI-calibrated timing.

This script:
1. Reads estimated_days from BLUEPRINT.yaml
2. Calculates AI-calibrated dates (22.8x speedup, 1.3x buffer)
3. Adds issues to GitHub Project (if not already added)
4. Sets Start Date and Target Date fields via GraphQL

Usage:
    ./populate-issue-dates.py --project-number 6 --owner IAMSamuelRodda --repo brand-forge
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional

import yaml

# AI Agent Timing Calibration Constants
AI_CALIBRATION_MULTIPLIER = 0.044  # 4.4% of human estimates (22.8x speedup)
BUFFER_MULTIPLIER = 1.3  # 30% buffer for uncertainty/blocked time


def load_blueprint(filepath: str) -> dict:
    """Load BLUEPRINT.yaml"""
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)


def calculate_ai_dates(estimated_days: float, cumulative_offset: float,
                       project_start: datetime) -> Dict[str, str]:
    """Calculate AI-calibrated start and target dates"""
    ai_duration = estimated_days * AI_CALIBRATION_MULTIPLIER * BUFFER_MULTIPLIER
    start_date = project_start + timedelta(days=cumulative_offset)
    target_date = start_date + timedelta(days=ai_duration)

    return {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'target_date': target_date.strftime('%Y-%m-%d'),
        'ai_duration_days': round(ai_duration, 2)
    }


def get_project_id(project_number: int, owner: str) -> Optional[str]:
    """Get project node ID"""
    query = '''
    query($owner: String!, $number: Int!) {
      user(login: $owner) {
        projectV2(number: $number) {
          id
        }
      }
    }
    '''

    result = subprocess.run(
        ['gh', 'api', 'graphql', '-f', f'query={query}',
         '-F', f'number={project_number}', '-f', f'owner={owner}'],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data.get('data', {}).get('user', {}).get('projectV2', {}).get('id')
    return None


def get_project_fields(project_id: str) -> Dict[str, str]:
    """Get project field IDs for Start Date and Target Date"""
    query = '''
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          fields(first: 20) {
            nodes {
              ... on ProjectV2Field {
                id
                name
                dataType
              }
            }
          }
        }
      }
    }
    '''

    result = subprocess.run(
        ['gh', 'api', 'graphql', '-f', f'query={query}',
         '-f', f'projectId={project_id}'],
        capture_output=True, text=True
    )

    field_map = {}
    if result.returncode == 0:
        data = json.loads(result.stdout)
        fields = data.get('data', {}).get('node', {}).get('fields', {}).get('nodes', [])
        for field in fields:
            if field.get('name') == 'Start Date' and field.get('dataType') == 'DATE':
                field_map['start_date'] = field['id']
            elif field.get('name') == 'Target Date' and field.get('dataType') == 'DATE':
                field_map['target_date'] = field['id']

    return field_map


def create_date_fields(project_number: int, owner: str) -> bool:
    """Create Start Date and Target Date fields if they don't exist"""
    print("📅 Creating date fields...")

    # Create Start Date field
    result = subprocess.run(
        ['gh', 'project', 'field-create', str(project_number),
         '--owner', owner, '--name', 'Start Date', '--data-type', 'DATE'],
        capture_output=True, text=True
    )
    if result.returncode != 0 and 'already exists' not in result.stderr:
        print(f"  ⚠️  Start Date: {result.stderr.strip()}")
    else:
        print(f"  ✓ Start Date field ready")

    # Create Target Date field
    result = subprocess.run(
        ['gh', 'project', 'field-create', str(project_number),
         '--owner', owner, '--name', 'Target Date', '--data-type', 'DATE'],
        capture_output=True, text=True
    )
    if result.returncode != 0 and 'already exists' not in result.stderr:
        print(f"  ⚠️  Target Date: {result.stderr.strip()}")
    else:
        print(f"  ✓ Target Date field ready")

    return True


def get_issue_project_item_id(issue_number: int, project_id: str,
                               owner: str, repo: str) -> Optional[str]:
    """Get project item ID for an issue (if it's in the project)"""
    query = '''
    query($owner: String!, $repo: String!, $issueNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issueNumber) {
          projectItems(first: 10) {
            nodes {
              id
              project {
                id
              }
            }
          }
        }
      }
    }
    '''

    result = subprocess.run(
        ['gh', 'api', 'graphql', '-f', f'query={query}',
         '-f', f'owner={owner}', '-f', f'repo={repo}',
         '-F', f'issueNumber={issue_number}'],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        data = json.loads(result.stdout)
        items = data.get('data', {}).get('repository', {}).get('issue', {}).get('projectItems', {}).get('nodes', [])
        for item in items:
            if item.get('project', {}).get('id') == project_id:
                return item['id']
    return None


def add_issue_to_project(issue_number: int, project_id: str,
                         owner: str, repo: str) -> Optional[str]:
    """Add issue to project and return project item ID"""
    # Get issue node ID first
    result = subprocess.run(
        ['gh', 'api', f'repos/{owner}/{repo}/issues/{issue_number}',
         '--jq', '.node_id'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return None

    issue_id = result.stdout.strip()

    # Add to project
    mutation = '''
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
          id
        }
      }
    }
    '''

    result = subprocess.run(
        ['gh', 'api', 'graphql', '-f', f'query={mutation}',
         '-f', f'projectId={project_id}', '-f', f'contentId={issue_id}'],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        data = json.loads(result.stdout)
        return data.get('data', {}).get('addProjectV2ItemById', {}).get('item', {}).get('id')
    return None


def update_date_field(project_id: str, item_id: str, field_id: str,
                      date_value: str) -> bool:
    """Update a date field for a project item"""
    mutation = '''
    mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: Date!) {
      updateProjectV2ItemFieldValue(
        input: {
          projectId: $projectId
          itemId: $itemId
          fieldId: $fieldId
          value: {date: $value}
        }
      ) {
        projectV2Item {
          id
        }
      }
    }
    '''

    result = subprocess.run(
        ['gh', 'api', 'graphql', '-f', f'query={mutation}',
         '-f', f'projectId={project_id}', '-f', f'itemId={item_id}',
         '-f', f'fieldId={field_id}', '-f', f'value={date_value}'],
        capture_output=True, text=True
    )

    return result.returncode == 0


def main():
    parser = argparse.ArgumentParser(
        description='Populate GitHub Project date fields with AI-calibrated dates'
    )
    parser.add_argument('--project-number', type=int, required=True,
                       help='GitHub Project number')
    parser.add_argument('--owner', required=True, help='Repository owner')
    parser.add_argument('--repo', required=True, help='Repository name')
    parser.add_argument('--blueprint', default='specs/BLUEPRINT.yaml',
                       help='Path to BLUEPRINT.yaml')
    parser.add_argument('--project-start-date', type=str, default=None,
                       help='Project start date (YYYY-MM-DD), defaults to today')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without making changes')

    args = parser.parse_args()

    # Parse project start date
    if args.project_start_date:
        project_start = datetime.strptime(args.project_start_date, '%Y-%m-%d')
    else:
        project_start = datetime.now()

    print(f"\n🚀 Populating dates for project #{args.project_number}")
    print(f"   Owner: {args.owner}")
    print(f"   Repo: {args.repo}")
    print(f"   Start Date: {project_start.strftime('%Y-%m-%d')}")
    print(f"   Calibration: {AI_CALIBRATION_MULTIPLIER} × {BUFFER_MULTIPLIER}")

    if args.dry_run:
        print("\n🔍 DRY RUN MODE - No changes will be made\n")

    # Load blueprint
    print(f"\n📖 Loading blueprint: {args.blueprint}")
    blueprint = load_blueprint(args.blueprint)

    # Get project ID
    print(f"\n🔍 Getting project ID...")
    project_id = get_project_id(args.project_number, args.owner)
    if not project_id:
        print(f"❌ Could not find project #{args.project_number}")
        sys.exit(1)
    print(f"   ✓ Project ID: {project_id}")

    # Create date fields if needed
    if not args.dry_run:
        create_date_fields(args.project_number, args.owner)

    # Get field IDs
    print(f"\n🔍 Getting date field IDs...")
    field_map = get_project_fields(project_id)
    if 'start_date' not in field_map or 'target_date' not in field_map:
        print(f"❌ Missing date fields. Found: {list(field_map.keys())}")
        sys.exit(1)
    print(f"   ✓ Start Date field ID: {field_map['start_date'][:12]}...")
    print(f"   ✓ Target Date field ID: {field_map['target_date'][:12]}...")

    # Calculate dates for all issues
    print(f"\n📊 Calculating AI-calibrated dates...")
    cumulative_days = 0.0
    issue_dates = {}  # Map issue number to dates

    # Normalize blueprint structure
    milestones = blueprint.get('milestones', {})

    for milestone_key, milestone_data in milestones.items():
        epics = milestone_data.get('epics', {})

        for epic_key, epic_data in epics.items():
            epic_start = cumulative_days

            # Process features
            for feature_key, feature_data in epic_data.items():
                if feature_key.startswith('feature_') and isinstance(feature_data, dict):
                    est_days = feature_data.get('estimated_days', 0)
                    if est_days > 0:
                        dates = calculate_ai_dates(est_days, cumulative_days, project_start)
                        # Store for later (we'll need to map epic/feature keys to issue numbers)
                        cumulative_days += dates['ai_duration_days']

    print(f"   Total projected duration: {cumulative_days:.1f} days")

    # Now populate dates for actual issues
    print(f"\n📝 Populating dates for issues...")

    # Read issue mapping from CONTRIBUTING or query GitHub
    # For now, we'll process sequentially starting from issue #1

    cumulative_days = 0.0
    issue_num = 1
    updated_count = 0

    # Process in order: Epic 1, Features 2-10, Epic 11, Features 12-23, etc.
    for milestone_key, milestone_data in milestones.items():
        epics = milestone_data.get('epics', {})

        for epic_key, epic_data in epics.items():
            epic_issue = issue_num
            epic_start_offset = cumulative_days
            issue_num += 1

            # Track epic dates (will set after processing all features)
            epic_feature_start = None
            epic_feature_end = None

            # Process features for this epic
            for feature_key, feature_data in epic_data.items():
                if feature_key.startswith('feature_') and isinstance(feature_data, dict):
                    feature_issue = issue_num
                    est_days = feature_data.get('estimated_days', 0)

                    if est_days > 0:
                        dates = calculate_ai_dates(est_days, cumulative_days, project_start)

                        # Track epic boundaries
                        if epic_feature_start is None:
                            epic_feature_start = dates['start_date']
                        epic_feature_end = dates['target_date']

                        print(f"  Issue #{feature_issue}: {feature_data.get('name', 'Unknown')[:50]}")
                        print(f"    {dates['start_date']} → {dates['target_date']} ({dates['ai_duration_days']} days)")

                        if not args.dry_run:
                            # Get or create project item ID
                            item_id = get_issue_project_item_id(
                                feature_issue, project_id, args.owner, args.repo
                            )

                            if not item_id:
                                item_id = add_issue_to_project(
                                    feature_issue, project_id, args.owner, args.repo
                                )

                            if item_id:
                                # Update start date
                                if update_date_field(project_id, item_id,
                                                    field_map['start_date'],
                                                    dates['start_date']):
                                    # Update target date
                                    if update_date_field(project_id, item_id,
                                                        field_map['target_date'],
                                                        dates['target_date']):
                                        updated_count += 1

                        cumulative_days += dates['ai_duration_days']

                    issue_num += 1

                    # Process tasks
                    for task_key, task_data in feature_data.items():
                        if task_key.startswith('task_') and isinstance(task_data, dict):
                            issue_num += 1

            # Now set epic dates (span of all its features)
            if epic_feature_start and epic_feature_end and not args.dry_run:
                print(f"  Epic #{epic_issue}: {epic_data.get('name', 'Unknown')[:50]}")
                print(f"    {epic_feature_start} → {epic_feature_end} (spans all features)")

                item_id = get_issue_project_item_id(
                    epic_issue, project_id, args.owner, args.repo
                )

                if not item_id:
                    item_id = add_issue_to_project(
                        epic_issue, project_id, args.owner, args.repo
                    )

                if item_id:
                    if update_date_field(project_id, item_id,
                                        field_map['start_date'],
                                        epic_feature_start):
                        if update_date_field(project_id, item_id,
                                            field_map['target_date'],
                                            epic_feature_end):
                            updated_count += 1

    print(f"\n✅ Complete!")
    if not args.dry_run:
        print(f"   Updated {updated_count} issues with dates")
    else:
        print(f"   Would update dates for ~{updated_count} issues")


if __name__ == '__main__':
    main()
