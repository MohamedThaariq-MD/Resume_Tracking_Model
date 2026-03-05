from parser import extract_skills

noisy_text = """
role##dmysqllinq##qllocationmonthslakhs##dbhandmysmon40kinternshipcompletionasp.netctcdetailsjenkinsvue.jsspringbootfoundationmvcgitandroid##ql serverexpressexpress.jsfrontendmongodbflutter##end developmentserverremotebackendexperiencesalary.netj2eemonthcriteriajavascripteligibilitydocumentationmariadb##pnodespring boottoolsstrongangularmobilekoa.jsreact.jsswaggersde
"""

sample_resume = """
Experienced Fullstack Software Engineer with 5 years of experience building scalable web applications.
Proficient in Python, Django, and React.js on the frontend.
Familiar with Docker, Kubernetes, and AWS deployment pipelines.
Strong understanding of SQL and NoSQL databases like MongoDB and PostgreSQL.
Used Git and GitHub for version control in Agile/Scrum environments.
"""

if __name__ == "__main__":
    print("-" * 40)
    print("Testing against noisy user string:")
    print("-" * 40)
    noisy_skills = extract_skills(noisy_text)
    print(noisy_skills)
    
    print("\n" + "-" * 40)
    print("Testing against standard clean resume:")
    print("-" * 40)
    clean_skills = extract_skills(sample_resume)
    print(clean_skills)
