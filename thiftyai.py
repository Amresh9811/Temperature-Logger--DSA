from collections import deque
import time
import random

class TemperatureLogger:
    """
    Real-time temperature logging system with efficient operations.
    
    Supports:
    - addReading(temp): Add new temperature reading
    - getAverage(k): Get average of last k readings  
    - getMaxWindow(k): Get maximum average over any window of k readings
    """
    
    def __init__(self):
        self.readings = []
        self.window_maxes = {}  # k -> maximum average for window size k
        self.window_tracking = {}  # k -> {'deque': deque, 'sum': current_sum}
        
    def addReading(self, temp: int):
        """
        Add a new temperature reading.
        
        Args:
            temp (int): Temperature reading between -10 and +10
            
        Raises:
            ValueError: If temperature is outside valid range
            
        Time Complexity: O(W) where W is number of unique window sizes tracked
        """
        if not isinstance(temp, int) or not (-10 <= temp <= 10):
            raise ValueError("Temperature must be an integer between -10 and +10")
        
        self.readings.append(temp)
        
        # Update all tracked sliding windows
        for k in list(self.window_tracking.keys()):
            tracker = self.window_tracking[k]
            window_deque = tracker['deque']
            
            # Add new reading
            window_deque.append(temp)
            tracker['sum'] += temp
            
            # Remove oldest if window exceeds size k
            if len(window_deque) > k:
                oldest = window_deque.popleft()
                tracker['sum'] -= oldest
            
            # Update maximum if we have a complete window
            if len(window_deque) == k:
                current_avg = tracker['sum'] / k
                self.window_maxes[k] = max(self.window_maxes.get(k, float('-inf')), current_avg)
    
    def getAverage(self, k: int):
        """
        Get average of the last k temperature readings.
        
        Args:
            k (int): Number of recent readings to average
            
        Returns:
            float: Average of last k readings
            
        Raises:
            ValueError: If k is invalid or insufficient readings
            
        Time Complexity: O(k)
        """
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k must be a positive integer")
        
        if k > len(self.readings):
            raise ValueError(f"Not enough readings. Have {len(self.readings)}, need {k}")
        
        last_k_readings = self.readings[-k:]
        return sum(last_k_readings) / k
    
    def getMaxWindow(self, k: int):
        """
        Get maximum average over any continuous window of k readings seen so far.
        
        Args:
            k (int): Window size
            
        Returns:
            float: Maximum average over any window of size k
            
        Raises:
            ValueError: If k is invalid or insufficient readings
            
        Time Complexity: O(n) for first call with new k, O(1) for subsequent calls
        """
        if not isinstance(k, int) or k <= 0:
            raise ValueError("k must be a positive integer")
        
        if k > len(self.readings):
            raise ValueError(f"Not enough readings. Have {len(self.readings)}, need {k}")
        
        # If first time tracking this window size, calculate historical maximum
        if k not in self.window_maxes:
            self._initialize_window_tracking(k)
        
        return self.window_maxes[k]
    
    def _initialize_window_tracking(self, k: int):
        """
        Initialize tracking for a new window size k.
        Calculates maximum average for all historical windows of size k.
        """
        max_avg = float('-inf')
        
        # Calculate max average for all possible windows of size k
        for i in range(len(self.readings) - k + 1):
            window_sum = sum(self.readings[i:i+k])
            avg = window_sum / k
            max_avg = max(max_avg, avg)
        
        self.window_maxes[k] = max_avg
        
        # Set up sliding window tracking for future readings
        last_k = self.readings[-k:] if len(self.readings) >= k else []
        self.window_tracking[k] = {
            'deque': deque(last_k),
            'sum': sum(last_k)
        }
    
    def get_stats(self):
        """Get current statistics about the logger."""
        return {
            'total_readings': len(self.readings),
            'tracked_windows': list(self.window_maxes.keys()),
            'latest_reading': self.readings[-1] if self.readings else None,
            'min_reading': min(self.readings) if self.readings else None,
            'max_reading': max(self.readings) if self.readings else None
        }


def test_basic_functionality():
    """Test basic operations"""
    print("Test 1: Basic Functionality")
    logger = TemperatureLogger()
    
    readings = [5, -2, 8, 1, -3, 7, 0, 4, -1, 6]
    for temp in readings:
        logger.addReading(temp)
    
    print(f"Added readings: {readings}")
    print(f"Last 3 average: {logger.getAverage(3):.2f}")
    print(f"Last 5 average: {logger.getAverage(5):.2f}")
    print(f"Max window of 3: {logger.getMaxWindow(3):.2f}")
    print(f"Max window of 5: {logger.getMaxWindow(5):.2f}")
    print("✅ Basic functionality test passed\n")


def test_edge_cases():
    """Test edge cases and error handling"""
    print("Test 2: Edge Cases")
    logger = TemperatureLogger()
    
    # Add some readings first
    for temp in [1, 2, 3, 4, 5]:
        logger.addReading(temp)
    
    # Test invalid k values
    try:
        logger.getAverage(0)
        print("❌ Should have raised error for k=0")
    except ValueError:
        print("✅ Correctly caught error for k=0")
    
    try:
        logger.getAverage(-1)
        print("❌ Should have raised error for k=-1")
    except ValueError:
        print("✅ Correctly caught error for k=-1")
    
    try:
        logger.getAverage(10)  # More than available readings
        print("❌ Should have raised error for k > readings")
    except ValueError:
        print("✅ Correctly caught error for k > available readings")
    
    # Test invalid temperature
    try:
        logger.addReading(15)
        print("❌ Should have raised error for temp=15")
    except ValueError:
        print("✅ Correctly caught error for invalid temperature")
    
    try:
        logger.addReading(-15)
        print("❌ Should have raised error for temp=-15")
    except ValueError:
        print("✅ Correctly caught error for invalid temperature")
    
    print("✅ Edge cases test passed\n")


def test_negative_numbers():
    """Test with all negative numbers"""
    print("Test 3: All Negative Numbers")
    logger = TemperatureLogger()
    
    neg_readings = [-5, -8, -2, -10, -1]
    for temp in neg_readings:
        logger.addReading(temp)
    
    print(f"Negative readings: {neg_readings}")
    avg = logger.getAverage(5)
    max_window = logger.getMaxWindow(3)
    print(f"Average of all: {avg:.2f}")
    print(f"Max window of 3: {max_window:.2f}")
    
    # Verify calculations
    expected_avg = sum(neg_readings) / 5
    assert abs(avg - expected_avg) < 0.001, f"Expected {expected_avg}, got {avg}"
    print("✅ Negative numbers test passed\n")


def test_mixed_numbers():
    """Test with mixed positive and negative numbers"""
    print("Test 4: Mixed Positive/Negative")
    logger = TemperatureLogger()
    
    mixed_readings = [10, -10, 5, -5, 8, -8, 3, -3]
    for temp in mixed_readings:
        logger.addReading(temp)
    
    print(f"Mixed readings: {mixed_readings}")
    avg = logger.getAverage(4)
    max_window = logger.getMaxWindow(4)
    print(f"Last 4 average: {avg:.2f}")
    print(f"Max window of 4: {max_window:.2f}")
    
    # Last 4 readings: [8, -8, 3, -3], average = 0
    expected_avg = (8 + (-8) + 3 + (-3)) / 4
    assert abs(avg - expected_avg) < 0.001, f"Expected {expected_avg}, got {avg}"
    print("✅ Mixed numbers test passed\n")


def test_single_reading():
    """Test with single reading"""
    print("Test 5: Single Reading")
    logger = TemperatureLogger()
    logger.addReading(7)
    
    avg = logger.getAverage(1)
    max_window = logger.getMaxWindow(1)
    print(f"Single reading: 7")
    print(f"Average of 1: {avg}")
    print(f"Max window of 1: {max_window}")
    
    assert avg == 7.0, f"Expected 7.0, got {avg}"
    assert max_window == 7.0, f"Expected 7.0, got {max_window}"
    print("✅ Single reading test passed\n")


def test_identical_readings():
    """Test with identical readings"""
    print("Test 6: Identical Readings")
    logger = TemperatureLogger()
    
    for _ in range(5):
        logger.addReading(3)
    
    avg = logger.getAverage(3)
    max_window = logger.getMaxWindow(3)
    print(f"All readings are 3")
    print(f"Average of 3: {avg}")
    print(f"Max window of 3: {max_window}")
    
    assert avg == 3.0, f"Expected 3.0, got {avg}"
    assert max_window == 3.0, f"Expected 3.0, got {max_window}"
    print("✅ Identical readings test passed\n")


def test_dynamic_tracking():
    """Test dynamic window tracking"""
    print("Test 7: Dynamic Window Tracking")
    logger = TemperatureLogger()
    
    dynamic_readings = [1, 5, 2, 8, 3, 7, 4, 6]
    print("Adding readings dynamically and tracking max window of size 3:")
    
    for i, temp in enumerate(dynamic_readings):
        logger.addReading(temp)
        if i >= 2:  # Can calculate window of 3
            current_avg = logger.getAverage(3)
            max_window = logger.getMaxWindow(3)
            print(f"  After adding {temp}: current_avg={current_avg:.2f}, max_window={max_window:.2f}")
    
    print("✅ Dynamic tracking test passed\n")


def test_performance():
    """Test performance with larger dataset"""
    print("Test 8: Performance Test (10,000 readings)")
    logger = TemperatureLogger()
    
    start_time = time.time()
    
    # Add 10,000 random readings
    for i in range(10000):
        temp = random.randint(-10, 10)
        logger.addReading(temp)
        
        # Occasionally query averages and max windows
        if i % 1000 == 0 and i > 0:
            logger.getAverage(min(100, i))
            logger.getMaxWindow(min(50, i))
    
    end_time = time.time()
    
    print(f"✅ Successfully processed 10,000 readings in {end_time - start_time:.3f} seconds")
    stats = logger.get_stats()
    print(f"✅ Final stats: {stats}")
    print("✅ Performance test passed\n")


def test_boundary_values():
    """Test with boundary temperature values"""
    print("Test 9: Boundary Values")
    logger = TemperatureLogger()
    
    # Test extreme values
    extreme_readings = [-10, 10, -10, 10, 0]
    for temp in extreme_readings:
        logger.addReading(temp)
    
    print(f"Extreme readings: {extreme_readings}")
    avg = logger.getAverage(5)
    max_window = logger.getMaxWindow(3)
    print(f"Average of all: {avg:.2f}")
    print(f"Max window of 3: {max_window:.2f}")
    
    expected_avg = sum(extreme_readings) / 5
    assert abs(avg - expected_avg) < 0.001, f"Expected {expected_avg}, got {avg}"
    print("✅ Boundary values test passed\n")


def run_all_tests():
    """Run all comprehensive tests"""
    print("=" * 60)
    print("RUNNING COMPREHENSIVE TEMPERATURE LOGGER TESTS")
    print("=" * 60)
    print()
    
    try:
        test_basic_functionality()
        test_edge_cases()
        test_negative_numbers()
        test_mixed_numbers()
        test_single_reading()
        test_identical_readings()
        test_dynamic_tracking()
        test_boundary_values()
        test_performance()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


def demo_usage():
    """Demonstrate practical usage"""
    print("\n" + "=" * 50)
    print("PRACTICAL USAGE DEMONSTRATION")
    print("=" * 50)
    
    # Create logger instance
    temp_logger = TemperatureLogger()
    
    # Simulate real-time temperature readings
    sample_readings = [3, -1, 5, 2, -4, 8, 0, 6, -2, 7, 1, -3, 9, 4, -1]
    
    print("\nSimulating real-time temperature logging:")
    for i, temp in enumerate(sample_readings):
        temp_logger.addReading(temp)
        print(f"Reading {i+1}: {temp}°C added")
        
        # Show analytics every few readings
        if i >= 4 and (i + 1) % 5 == 0:
            avg_5 = temp_logger.getAverage(5)
            max_window_5 = temp_logger.getMaxWindow(5)
            print(f"  → Last 5 average: {avg_5:.2f}°C")
            print(f"  → Max 5-reading window: {max_window_5:.2f}°C")
            print()
    
    print(f"Final statistics:")
    print(f"Total readings: {len(temp_logger.readings)}")
    print(f"Overall average: {sum(temp_logger.readings) / len(temp_logger.readings):.2f}°C")
    print(f"Last 10 average: {temp_logger.getAverage(10):.2f}°C")
    print(f"Max window of 10: {temp_logger.getMaxWindow(10):.2f}°C")


# Main execution
if __name__ == "__main__":
    # Run comprehensive tests
    run_all_tests()
    
    # Show practical demonstration
    demo_usage()