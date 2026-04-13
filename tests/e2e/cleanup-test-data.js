#!/usr/bin/env node
/**
 * Cleanup script to remove E2E test data from the database.
 * This script deletes all tasks with titles containing 'E2E' or '测试' (test).
 *
 * WARNING: This only works against an API that supports DELETE operations.
 * Do NOT run this against production unless absolutely necessary!
 */

const API_BASE_URL = process.env.API_BASE_URL || 'http://localhost:8000/api';

async function cleanupTestData() {
  console.log(`Starting cleanup of test data from ${API_BASE_URL}...`);

  try {
    // Get all tasks
    const response = await fetch(`${API_BASE_URL}/tasks`);
    if (!response.ok) {
      console.error(`Failed to fetch tasks: ${response.status} ${response.statusText}`);
      return;
    }

    const data = await response.json();
    const tasks = data.tasks || data || [];

    // Filter tasks that look like test data
    const testTasks = tasks.filter(task => {
      const title = (task.title || '').toLowerCase();
      return title.includes('e2e') ||
             title.includes('测试') ||
             title.includes('test') ||
             title.includes('mock');
    });

    console.log(`Found ${testTasks.length} test task(s) to delete.`);

    // Delete each test task
    let deletedCount = 0;
    for (const task of testTasks) {
      try {
        const deleteResponse = await fetch(`${API_BASE_URL}/tasks/${task.id}`, {
          method: 'DELETE',
        });

        if (deleteResponse.ok) {
          deletedCount++;
          console.log(`Deleted task: ${task.title} (ID: ${task.id})`);
        } else {
          console.warn(`Failed to delete task ${task.id}: ${deleteResponse.status}`);
        }
      } catch (error) {
        console.error(`Error deleting task ${task.id}:`, error.message);
      }
    }

    console.log(`Cleanup complete. Deleted ${deletedCount} of ${testTasks.length} test tasks.`);

    if (deletedCount < testTasks.length) {
      process.exit(1);
    }
  } catch (error) {
    console.error('Error during cleanup:', error.message);
    process.exit(1);
  }
}

// Run cleanup
cleanupTestData();
