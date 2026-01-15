curl -X POST "http://localhost:5128/api/Navigator/analyze/gap"      -H "Content-Type: application/json"      -d '{
           "userProfile": { 
               "skills": ["C#", "SQL", "DotNet"], 
               "level": "Mid",
               "yearsOfExperience": 3,
               "profileSeniorityScore": 0.5
           },
           "jobDescription": {
               "skills": ["C#", "SQL", "Azure", "Microservices"], 
               "level": "Senior",
               "yearsOfExperience": 5,
               "profileSeniorityScore": 0.8
           }
         }'
