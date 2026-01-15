import unittest
from processing.text_parser import TextProcessor
from core.taxonomy import TaxonomyManager

class TestNormalizationExhaustive(unittest.TestCase):
    def setUp(self):
        # We assume TaxonomyManager loads the updated taxonomyAlias.json
        # Force cache clear just in case (though separate process usually)
        TaxonomyManager._ALIAS_MAP_CACHE = None
        TaxonomyManager._TAXONOMY_CACHE = None
        
        self.alias_map = TaxonomyManager.get_alias_map()
        self.matchable_terms = TaxonomyManager.get_matchable_terms()

    def test_dotnet_start_of_string(self):
        # ".Net" (case insensitive) -> matches canonical '.net'
        # Edge case: finding dot at start of word.
        text = ".Net Core is great."
        skills = TextProcessor.extract_skills(text, self.matchable_terms, self.alias_map)
        print(f"Debug .Net: {skills}")
        self.assertIn('.net', skills)

    def test_cpp_plus_signs(self):
        # "C++" -> matches 'cpp'
        # Edge case: + sign is regex special char.
        text = "Looking for a C++ developer."
        skills = TextProcessor.extract_skills(text, self.matchable_terms, self.alias_map)
        # canonical for C++ is 'cpp' in my taxonomy?
        # Let's verify what 'c++' maps to.
        canonical = self.alias_map.get('c++', 'c++')
        print(f"Debug C++ maps to: {canonical}")
        self.assertIn(canonical, skills)

    def test_mpc_acronym(self):
        # "MPC" -> matches 'mpc'
        text = "Secure MPC protocols."
        skills = TextProcessor.extract_skills(text, self.matchable_terms, self.alias_map)
        self.assertIn('mpc', skills)

    def test_gen_ai_multi_word(self):
        # "gen ai" -> matches 'generative_ai'
        # Edge case: space in middle. Masking "gen ai" prevents "ai" match? 
        # (Though 'ai' might not be a single term, 'gen' might not be either)
        text = "Specialist in Gen AI and LLMs."
        skills = TextProcessor.extract_skills(text, self.matchable_terms, self.alias_map)
        
        canonical = self.alias_map.get('gen ai', 'gen ai') # should be generative_ai
        print(f"Debug 'gen ai' maps to: {canonical}")
        
        self.assertIn('generative_ai', skills)
        self.assertIn('llm', skills)

    def test_csharp_hash(self):
        # "C#" -> matches 'csharp'
        # Edge case: # is regex safe usually, but word boundary is tricky.
        text = "Coding in C#."
        skills = TextProcessor.extract_skills(text, self.matchable_terms, self.alias_map)
        self.assertIn('csharp', skills)

    def test_type_script_split(self):
        # "type script" -> matches 'typescript'
        text = "Writing Type Script code."
        skills = TextProcessor.extract_skills(text, self.matchable_terms, self.alias_map)
        self.assertIn('typescript', skills)

    def test_embedded_dot_prevention(self):
        # ".Net" matching inside "vb.net"? 
        # If "vb.net" is in taxonomy, it should be matched first (longer).
        pass

if __name__ == '__main__':
    unittest.main()
