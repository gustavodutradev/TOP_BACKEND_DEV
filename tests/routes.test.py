from app.api.routes import get_suitability
from unittest.mock import patch
from app.api.routes import get_suitability
from unittest.mock import patch
from threading import Thread

def test_get_suitability_not_found():
    with patch('services.requests_service.RequestsService.get_suitability') as mock_get_suitability:
        mock_get_suitability.return_value = None

        response = get_suitability('non_existent_account')
        assert response.status_code == 404
        

def test_get_suitability_concurrent_requests():
    with patch('services.requests_service.RequestsService.get_suitability') as mock_get_suitability:
        mock_get_suitability.return_value = {'account_number': '123456789', 'suitability': 'High'}

        account_number = '123456789'
        threads = []

        for _ in range(5):  # Simulate concurrent requests
            t = Thread(target=get_suitability, args=(account_number,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert mock_get_suitability.call_count == 5
                
def test_get_suitability_requests_service_unavailable():
    with patch('app.api.routes.requests_service.get_suitability') as mock_get_suitability:
        mock_get_suitability.side_effect = Exception('Requests service is unavailable')
        
        response = get_suitability('non_existent_account')
        assert response.status_code == 50
def test_get_suitability_valid_account_number():
    with patch('app.api.routes.requests_service.RequestsService.get_suitability') as mock_get_suitability:
        mock_get_suitability.return_value = {'account_number': '123456789', 'suitability': 'High'}

        response = get_suitability('123456789')
        assert response.status_code == 200
        assert response.json == {'account_number': '123456789', 'suitability': 'High'}

def test_get_suitability_empty_response():
    with patch('app.api.routes.requests_service.RequestsService.get_suitability') as mock_get_suitability:
        mock_get_suitability.return_value = None

        response = get_suitability('non_existent_account')
        assert response.status_code == 200
        assert response.json == {}