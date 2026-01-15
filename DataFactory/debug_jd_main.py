from utils.text_processor import TextProcessor
from utils.taxonomy_manager import TaxonomyManager

jd_text = """About the job
Overview
Microsoft Viva Insights (also known as Copilot Analytics) empowers organizations to thrive in the era of AI-powered work. As part of 
     Microsoft 365 Copilot, it delivers privacy-protected, data-driven insights through a unified experience that helps organizations maximize the impact of their workforce by
     understanding and accelerating the adoption of Copilot and Agents.
Our team builds this platform using large scale data systems to surface actionable insights from 
     collaboration and business signals. We are hiring a Senior Software Engineer to help deliver data platform which helps scale this experience to planet scale, to realize 
     potential by unlocking the full value of Microsoft Copilot.
In the fast moving world of AI innovation, we operate with a startup mindset - agile, customer-obsessed, and 
     deeply collaborative. Our inclusive, growth-oriented culture is grounded in Microsoft’s mission to empower every person and organization on the planet to achieve 
     more.
Microsoft’s mission is to empower every person and every organization on the planet to achieve more. As employees we come together with a growth mindset, innovate 
     empower others, and collaborate to realize our shared goals. Each day we build on our values of respect, integrity, and accountability to create a culture of inclusion 
     where everyone can thrive at work and beyond.
Responsibilities
Running a global world class service that is tightly integrated with mission critical productivity apps 
     with millions of active users presents broad and evolving challenges. We are constantly in need of improving our platform and cloud services to meet the growing demands o
     a large user base that are rapidly expanding. We have complex multi-tiered applications running off distributed micro-services, handling billions of user interactions eve
     day, generating petabytes of data that require analysis and transformation, spanned across hundreds of thousands of machines. As a Senior Software Engineer, your key 
     responsibilities include the following:
Building future looking features in the platform which provide value to customers.
Modernizing our systems to ensure that our developers can work with the newest and best technology.
Refactoring and optimizing our computations and framework to improve our performance and scalability so that we 
     can deliver cost-effective features. 
Developing tools to analyze, monitor and recover our services to increase the resiliency of our services.
Improving our engineerin
     systems to ensure that our growing and global development team can build, deploy and manage our service in a secure and compliant manner.
Build and improve systems that 
     enable big data analysis to measure user and organizational productivity and customer engagement.
Qualifications
Required Qualifications:
Bachelor's Degree in Computer
     Science or related technical field AND 4+ years technical engineering experience with coding in languages including, but not limited to, C, C++, C#, Java, JavaScript, or 
     Python
OR equivalent experience.
4+ years of hands-on software design and coding experience.
Proficiency in object-oriented development, with C# and .Net Framework 
     (preferred) or any other object-oriented programming languages such as Java, C++ or related.
Strong computer science fundamentals and proven algorithm design 
     capability.
Good technical, cross group collaboration and communication skills.
Hands-on experience in architectural design and large-scale systems.
Other 
     Requirements
Ability to meet Microsoft, customer and/or government security screening requirements are required for this role. These requirements include but are not limited to, the following specialized security screenings:
Microsoft Cloud Background Check: This position will be required to pass the Microsoft Cloud background check 
     upon hire/transfer and every two years thereafter.
Preferred Qualifications
Master's Degree in Computer Science or related technical field AND 6+ years technical engineering experience with coding in languages including, but not limited to, C, C++, C#, Java, JavaScript, or Python
OR Bachelor's Degree in Computer Science or relate
     technical field AND 8+ years technical engineering experience with coding in languages including, but not limited to, C, C++, C#, Java, JavaScript, or Python 
OR 
     equivalent experience.
#SeniorSoftwareEngineer
This position will be open for a minimum of 5 days, with applications accepted on an ongoing basis until the position is 
     filled.
Microsoft is an equal opportunity employer. All qualified applicants will receive consideration for employment without regard to age, ancestry, citizenship, colo
     family or medical care leave, gender identity or expression, genetic information, immigration status, marital status, medical condition, national origin, physical or ment
     disability, political affiliation, protected veteran or military status, race, ethnicity, religion, sex (including pregnancy), sexual orientation, or any other 
     characteristic protected by applicable local laws, regulations and ordinances. If you need assistance with religious accommodations and/or a reasonable accommodation due 
     a disability during the application process, read more about requesting accommodations.
"""

def analyze():
    matchable_terms = TaxonomyManager.get_matchable_terms()
    alias_map = TaxonomyManager.get_alias_map()
    
    # 1. Seniority
    lines = jd_text.split('\n')
    title = lines[0] # "About the job" -> Wait, lines[0] might not be title.
    # The actual title is likely "Senior Software Engineer" mentioned inside, or user didn't provide title on first line.
    # TextProcessor.detect_seniority looks at `title` arg separately.
    # I'll scan the text for a likely title or just pass empty.
    # However, JD says "We are hiring a Senior Software Engineer".
    # And "#SeniorSoftwareEngineer".
    
    seniority = TextProcessor.detect_seniority("Senior Software Engineer", jd_text)
    
    # 2. Skills
    skills = TextProcessor.extract_skills(jd_text, matchable_terms, alias_map)
    
    print("\n--- Analysis Result ---")
    print(f"Seniority Level: {seniority['level']} (Score: {seniority['score']})")
    print(f"Is Senior: {seniority['is_senior']}")
    print(f"Found Skills ({len(skills)}):")
    for s in sorted(skills):
        print(f" - {s}")

if __name__ == "__main__":
    analyze()
