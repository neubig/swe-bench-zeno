"""Test visualization code."""

import os
import tempfile
import json
import pandas as pd
from unittest.mock import patch, MagicMock
from visualize_results import visualise_swe_bench, visualize_aider_bench


def test_visualise_swe_bench():
    """Test swe-bench visualization."""
    # Create mock data
    data = [
        ("test-1", "Fix this bug", True),
        ("test-2", "Add this feature", False),
    ]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        for entry in data:
            json.dump({"id": entry[0], "problem_statement": entry[1], "resolved": entry[2]}, f)
            f.write('\n')
        temp_file = f.name

    try:
        # Mock ZENO_API_KEY and ZenoClient
        os.environ["ZENO_API_KEY"] = "test_key"
        mock_client = MagicMock()
        mock_project = MagicMock()
        mock_client.create_project.return_value = mock_project
        
        with patch('zeno_client.ZenoClient', return_value=mock_client):
            # Run visualization
            visualise_swe_bench([temp_file])
            
            # Verify that create_project was called with the correct view
            mock_client.create_project.assert_called_once()
            args = mock_client.create_project.call_args[1]
            assert args["view"]["data"]["type"] == "message"
            assert args["view"]["data"]["content"]["type"] == "markdown"
            assert args["view"]["data"]["role"] == "user"
            assert args["view"]["output"]["type"] == "message"
            assert args["view"]["output"]["content"]["type"] == "markdown"
            assert args["view"]["output"]["role"] == "assistant"
            
            # Verify that upload_dataset and upload_system were called
            mock_project.upload_dataset.assert_called_once()
            mock_project.upload_system.assert_called_once()
            
            # Verify that the dataset has the correct format
            df_data = mock_project.upload_dataset.call_args[0][0]
            assert isinstance(df_data["problem_statement"].iloc[0], dict)
            assert "text" in df_data["problem_statement"].iloc[0]
            assert "sections" in df_data["problem_statement"].iloc[0]
            assert len(df_data["problem_statement"].iloc[0]["sections"]) == 1
            assert df_data["problem_statement"].iloc[0]["sections"][0]["title"] == "Problem"
            assert df_data["problem_statement"].iloc[0]["sections"][0]["content"] == "Fix this bug"
        
    finally:
        os.unlink(temp_file)


def test_visualize_aider_bench():
    """Test aider-bench visualization."""
    # Create mock data
    data = [
        {
            "id": "test-1",
            "instruction": "Fix the bug",
            "resolved": True,
            "test_cases": "test case 1",
            "tests": "test 1",
            "trajectory": [
                {
                    "action": "action1",
                    "code": "code1",
                    "thought": "thought1",
                    "observation": "obs1"
                }
            ]
        },
        {
            "id": "test-2",
            "instruction": "Add feature",
            "resolved": False,
            "test_cases": "test case 2",
            "tests": "test 2",
            "trajectory": [
                {
                    "action": "action2",
                    "code": "code2",
                    "thought": "thought2",
                    "observation": "obs2"
                }
            ]
        }
    ]
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        for entry in data:
            json.dump(entry, f)
            f.write('\n')
        temp_file = f.name

    try:
        # Mock ZENO_API_KEY and ZenoClient
        os.environ["ZENO_API_KEY"] = "test_key"
        mock_client = MagicMock()
        mock_project = MagicMock()
        mock_client.create_project.return_value = mock_project
        
        with patch('zeno_client.ZenoClient', return_value=mock_client):
            # Run visualization
            visualize_aider_bench([temp_file])
            
            # Verify that create_project was called with the correct view
            mock_client.create_project.assert_called_once()
            args = mock_client.create_project.call_args[1]
            assert args["view"]["data"]["type"] == "message"
            assert args["view"]["data"]["content"]["type"] == "markdown"
            assert args["view"]["data"]["role"] == "user"
            assert args["view"]["output"]["type"] == "message"
            assert args["view"]["output"]["content"]["type"] == "markdown"
            assert args["view"]["output"]["role"] == "assistant"
            
            # Verify that upload_dataset and upload_system were called
            mock_project.upload_dataset.assert_called_once()
            mock_project.upload_system.assert_called_once()
            
            # Verify that the output contains the expected markdown format
            output_data = mock_project.upload_system.call_args[1]
            print("Output data:", output_data)
            
            # Get the DataFrame from the first positional argument
            df = mock_project.upload_system.call_args[0][0]
            print("DataFrame:", df)
            
            # Verify that the DataFrame contains the expected JSON format
            output = df["agent output"].iloc[0]
            assert output["text"] == ""
            assert len(output["sections"]) == 4
            assert output["sections"][0]["title"] == "Resolved"
            assert output["sections"][0]["content"] == "True"
            assert output["sections"][1]["title"] == "Test Cases"
            assert output["sections"][1]["content"] == "test case 1"
            assert output["sections"][2]["title"] == "Tests"
            assert output["sections"][2]["content"] == "test 1"
            assert output["sections"][3]["title"] == "Agent Trajectory"
            assert "### Step 1" in output["sections"][3]["content"]
            assert "Action: action1" in output["sections"][3]["content"]
            assert "Code: code1" in output["sections"][3]["content"]
            assert "Thought: thought1" in output["sections"][3]["content"]
            assert "Observation: obs1" in output["sections"][3]["content"]
        
    finally:
        os.unlink(temp_file)