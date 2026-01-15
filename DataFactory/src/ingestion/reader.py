from typing import List

class Reader:
    """!
    @brief Operations for reading data.
    """

    @staticmethod
    def load_raw_jds(file_path: str = "data/input/raw_jds.txt", delimiter: str = "###END###") -> List[str]:
        """!
        @brief Loads and segments raw job description data.
        
        @param file_path Path to the raw text file.
        @param delimiter The string marker used to separate distinct JDs.
        @return A list of strings, where each string is one full job description.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content: str = f.read()
                raw_segments: List[str] = content.split(delimiter)
                jds: List[str] = []
                for segment in raw_segments:
                    cleaned_segment: str = segment.strip()
                    if cleaned_segment:
                        jds.append(cleaned_segment)

                return jds
                
        except FileNotFoundError:
            print(f"❌ Error: {file_path} not found!")
            return []
