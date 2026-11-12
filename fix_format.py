import re

with open('sid.tex', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix the Literature Review Table
def replace_lit_table(match):
    table_content = match.group(0)
    # Replace \small with \scriptsize
    table_content = table_content.replace('\\small', '\\scriptsize')
    # Add \newpage before the table if it's not already there
    return '\\newpage\n' + table_content

text = re.sub(r'\\begin\{table\}\[H\].*?\\caption\{Foundational Literature Review\}.*?\\end\{table\}', replace_lit_table, text, flags=re.DOTALL)

# 2. Re-write the Empirical GUI Validation section
new_gui_section = r'''\section{Empirical GUI Validation}
To visually validate the capabilities of the Cognitive Collaborator framework, we present several empirical outcomes demonstrating its cross-application tracking, Rationale Trace Logging, and generative user interface generation.

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\textwidth]{"screen_shots/WhatsApp Image 2026-05-04 at 02.32.22 (1).jpeg"}
    \caption{Ambient UI Overlay operating seamlessly on top of a third-party web browser. The agent actively interprets the user's natural language request (finding movies in Pune) and executes cross-application web operations directly within the target environment.}
    \label{fig:ambient_overlay}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\textwidth]{"screen_shots/WhatsApp Image 2026-05-04 at 02.32.23.jpeg"}
    \caption{Structured Generative UI table organizing unstructured web data (Movies Currently Playing in Pune). This eliminates the need for manual copy-pasting by presenting the requested information in an immediately actionable format.}
    \label{fig:movies_table}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\textwidth]{"screen_shots/WhatsApp Image 2026-05-04 at 02.32.22.jpeg"}
    \caption{Generative UI widget displaying dynamic business intelligence metrics (Total Revenue, Total Profit). The agent proactively synthesizes the data and suggests highly relevant follow-up analytical queries to maintain workflow continuity.}
    \label{fig:bi_metrics}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\textwidth]{"screen_shots/WhatsApp Image 2026-05-04 at 02.32.23 (2).jpeg"}
    \caption{Dynamically generated interactive data visualization widget (Revenue Distribution by Continent). By responding to user queries with structured graphical representations instead of raw text, the agent drastically reduces cognitive load.}
    \label{fig:pie_chart}
\end{figure}

\begin{figure}[H]
    \centering
    \includegraphics[width=0.6\textwidth]{"screen_shots/WhatsApp Image 2026-05-04 at 02.32.24.jpeg"}
    \caption{Complex tabular widget synthesizing multi-dimensional enterprise data (Top 5 Customers by Spend). The agent securely extracts, parses, and displays high-value internal data fields across multiple dimensions directly within the ambient UI.}
    \label{fig:customers_table}
\end{figure}
'''

start_str = r'\section{Empirical GUI Validation}'
end_str = r'\chapter{Conclusion and Future Scope}'

pattern = re.compile(re.escape(start_str) + r'.*?(?=' + re.escape(end_str) + ')', re.DOTALL)
text = pattern.sub(new_gui_section + '\n\n', text)

with open('sid.tex', 'w', encoding='utf-8') as f:
    f.write(text)

print('Updated sid.tex')
