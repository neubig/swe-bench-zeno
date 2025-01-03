import os
import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from data_utils import load_data, extract_conversation, load_data_aider_bench, get_model_name_aider_bench
from visualize_results import visualise_swe_bench, visualize_aider_bench

class TestVisualization(unittest.TestCase):
    def setUp(self):
        self.test_data_dir = os.path.join(os.path.dirname(__file__), 'test_data')
        self.test_file = os.path.join(self.test_data_dir, 'test_output.jsonl')
        self.test_aider_file = os.path.join(self.test_data_dir, 'test_aider_output.jsonl')

    def test_extract_conversation(self):
        # Test with list of dictionaries
        history = [
            {"source": "user", "message": "Hello"},
            {"source": "agent", "message": "Hi"}
        ]
        expected = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"}
        ]
        self.assertEqual(extract_conversation(history), expected)

        # Test with empty list
        self.assertEqual(extract_conversation([]), [])

        # Test with invalid input
        self.assertEqual(extract_conversation("not a list"), [])

    def test_load_data(self):
        data = load_data(self.test_file)
        self.assertEqual(len(data), 2)
        
        # Check first entry
        self.assertEqual(data[0][0], "test-instance-1")  # instance_id
        self.assertEqual(data[0][1], "Fix the bug in test_file.py")  # problem_statement
        self.assertEqual(data[0][2], 1)  # resolved status
        self.assertEqual(len(data[0][3]), 2)  # conversation history

        # Check second entry
        self.assertEqual(data[1][0], "test-instance-2")
        self.assertEqual(data[1][1], "Add a new feature")
        self.assertEqual(data[1][2], 0)
        self.assertEqual(len(data[1][3]), 2)

    @patch.dict('os.environ', {'Zeno_Key': 'test_key'})
    @patch('zeno_client.ZenoClient')
    def test_visualise_swe_bench(self, mock_zeno_client):
        # Create mock objects
        mock_client = MagicMock()
        mock_project = MagicMock()
        mock_zeno_client.return_value = mock_client
        mock_client.create_project.return_value = mock_project

        # Call the function
        visualise_swe_bench([self.test_file])

        # Verify ZenoClient was initialized
        mock_zeno_client.assert_called_once_with('test_key')

        # Verify project was created with correct parameters
        mock_client.create_project.assert_called_once()
        project_args = mock_client.create_project.call_args[1]
        self.assertEqual(project_args['name'], 'SWE-bench Conversation Analysis')
        self.assertEqual(project_args['public'], False)

        # Verify dataset was uploaded
        mock_project.upload_dataset.assert_called_once()
        df_args = mock_project.upload_dataset.call_args[1]
        self.assertIsInstance(df_args['df_data'], pd.DataFrame)
        self.assertEqual(df_args['id_column'], 'id')
        self.assertEqual(df_args['data_column'], 'data')

        # Verify system was uploaded
        mock_project.upload_system.assert_called_once()
        system_args = mock_project.upload_system.call_args[1]
        self.assertIsInstance(system_args['df_system'], pd.DataFrame)
        self.assertEqual(system_args['id_column'], 'id')
        self.assertEqual(system_args['output_column'], 'output')

    def test_load_data_aider_bench(self):
        data = load_data_aider_bench(self.test_aider_file)
        self.assertEqual(len(data), 2)
        
        # Check first entry
        self.assertEqual(data[0][0], "test-instance-1")  # instance_id
        self.assertEqual(data[0][1], "Fix the bug")  # instruction
        self.assertEqual(data[0][2], 1)  # resolved status
        self.assertEqual(data[0][3], "...")  # test_cases
        self.assertEqual(data[0][4], "def test_fix(): assert True")  # tests
        self.assertEqual(len(data[0][5]), 1)  # agent_trajectory

        # Check second entry
        self.assertEqual(data[1][0], "test-instance-2")
        self.assertEqual(data[1][1], "Add feature")
        self.assertEqual(data[1][2], 0)
        self.assertEqual(data[1][3], ".F")
        self.assertEqual(data[1][4], "def test_add(): assert False")
        self.assertEqual(len(data[1][5]), 1)

    def test_get_model_name_aider_bench(self):
        model_name = get_model_name_aider_bench(self.test_aider_file)
        self.assertEqual(model_name, "gpt-4")

    @patch.dict('os.environ', {'ZENO_API_KEY': 'test_key'})
    @patch('zeno_client.ZenoClient')
    def test_visualize_aider_bench(self, mock_zeno_client):
        # Create mock objects
        mock_client = MagicMock()
        mock_project = MagicMock()
        mock_zeno_client.return_value = mock_client
        mock_client.create_project.return_value = mock_project

        # Call the function
        visualize_aider_bench([self.test_aider_file])

        # Verify ZenoClient was initialized
        mock_zeno_client.assert_called_once_with('test_key')

        # Verify project was created with correct parameters
        mock_client.create_project.assert_called_once()
        project_args = mock_client.create_project.call_args[1]
        self.assertEqual(project_args['name'], 'Aider Bench Code Editing Visualization')
        self.assertEqual(project_args['public'], False)

        # Verify dataset was uploaded
        mock_project.upload_dataset.assert_called_once()
        df_args = mock_project.upload_dataset.call_args[1]
        self.assertIsInstance(df_args['df_data'], pd.DataFrame)
        self.assertEqual(df_args['id_column'], 'id')
        self.assertEqual(df_args['data_column'], 'instruction')

        # Verify system was uploaded
        mock_project.upload_system.assert_called_once()
        system_args = mock_project.upload_system.call_args[1]
        self.assertIsInstance(system_args['df_system'], pd.DataFrame)
        self.assertEqual(system_args['id_column'], 'id')
        self.assertEqual(system_args['output_column'], 'agent output')

if __name__ == '__main__':
    unittest.main()