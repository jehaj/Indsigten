import subprocess
import os

class RipgrepSearcher:
    def search(self, query, search_dir):
        if not os.path.exists(search_dir):
            return []
            
        result = subprocess.run(
            ["rg", "--line-number", "--with-filename", "--no-heading", query, search_dir],
            capture_output=True,
            text=True,
            check=False
        )
        
        results = []
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                parts = line.split(':', 2)
                if len(parts) == 3:
                    results.append({
                        'file': parts[0],
                        'line': int(parts[1]),
                        'text': parts[2].strip()
                    })
        return results
