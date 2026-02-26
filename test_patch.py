import sys
from resilient_engine import StreamWrapper

def test_stream_wrapper():
    print("Testing StreamWrapper...")
    # Wrap a mock object to test
    class MockStream:
        def write(self, data):
            print(f"Mock wrote: {data.strip()}")
        def flush(self):
            print("Mock flushed.")
            raise OSError(22, "Invalid argument") # Simulate the error
            
    wrapped = StreamWrapper(MockStream())
    
    print("1. Writing normally...")
    wrapped.write("Hello\n")
    
    print("2. Flushing (should catch Errno 22)...")
    try:
        wrapped.flush()
        print("Success: OSError 22 was caught and silenced.")
    except Exception as e:
        print(f"Failure: Wrapper did not catch {e}")

if __name__ == "__main__":
    test_stream_wrapper()
