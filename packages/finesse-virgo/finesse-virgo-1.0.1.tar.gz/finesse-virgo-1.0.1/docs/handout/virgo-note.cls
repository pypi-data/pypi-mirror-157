% --- identification
\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{virgo-note}[2001/03/03 v0.1 LaTeX2e Virgo-note document class]

% --- using pkgs
\RequirePackage{fancyhdr}
\RequirePackage{lastpage}

% --- define options
\newif\if@color\@colorfalse
\newif\if@pdf\@pdffalse
\DeclareOption{color}{\@colortrue}
\DeclareOption{pdftex}{\@pdftrue}
\DeclareOption{twocolumn}{\OptionNotUsed}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\if@pdf
\RequirePackage[pdftex]{graphicx}
\else
\RequirePackage{graphicx}
\fi

\LoadClass[a4paper]{article}

\topmargin -15mm
\headsep 10mm
\headheight 23mm

%%\footheight 0mm

\textheight225mm
%\textheight230mm
\textwidth170mm

\hoffset 0mm
\voffset 0mm
%  modif centrage Coulon (papier A4, pas Letter) :
\oddsidemargin  -5mm
\evensidemargin -5mm

\leftmargin 20mm
\rightmargin 20mm

% --- load class

% color is switched on, use the color package
\if@color
\RequirePackage{color}
\fi%color

\def\issue#1{\gdef\@issue{#1}}
\def\@issue{\@latex@error{No \noexpand\issue given}\@ehc}
\def\refnum#1{\gdef\@refnum{#1}}
\def\@refnum{\@latex@error{No \noexpand\refnum given}\@ehc}
\def\shorttitle#1{\gdef\@shorttitle{#1}}
\def\@shorttitle{\@latex@error{No \noexpand\shorttitle given}\@ehc}

\renewcommand\maketitle{
\begin{titlepage}\begin{center}
%\begin{tabular}{ccc}
%\\
% {\Large CNRS} & \hspace{3cm} & {\Large INFN} \\
% {\small{\it Centre National de la Recherche Scientifique}} & &
%{\small{\it Istituto Nazionale di Fisica Nucleare}}\\
%\end{tabular}
\ \\
\vskip 4cm
{\begin{picture}(0,0)
\if@color
\put(-100,0){\includegraphics[height=14mm]{virgolog3}}
\else
\put(-100,0){\includegraphics[height=14mm]{virgolog3_bw}}
\fi
\end{picture}}
\vskip2cm
   {\LARGE \bf \@title \par}%
   \vskip 3em%
   {\sf \LARGE \@refnum \par}%
   \vskip 3em%
   {\large
     \lineskip .75em%
     \begin{tabular}[t]{c}%
       \@author
     \end{tabular}\par}%
   \vskip 1.5em%
   {\normalsize \textit{Issue:}~ \@issue \par}%
   {\normalsize \textit{Date:}~ \@date \par}%
   \vfil\null
{\small\vfill
Nikhef Institute of Subatomic Physics, Science Park 105, 1098 XG, Amsterdam (NL) \\
 Telephone +31 (0) 20 592 2000 * FAX   +31 (0) 20 592 5155 * Email: abianchi@nikhef.nl\\
\url{https://www.nikhef.nl/}
} \end{center}
\end{titlepage}
}

\pagestyle{fancy}
\lhead{\setlength{\unitlength}{1mm}
\begin{picture}(0,0)
\if@color
\put(0,1){\includegraphics[height=9mm]{./virgolog3}}
\else
\put(0,2){\includegraphics[height=9mm]{virgolog3_bw}}
\fi
\end{picture}}

\chead{
%\begin{picture}(0,0)\put(-160,12){\makebox(50,0)[lb]{\large \@shorttitle}}\end{picture}
\centerline{\textsf{\@shorttitle}}
}

%\chead{
%\parbox[b][][c]{8cm}{\textsf{\@shorttitle}}
%}

%\rhead{\begin{picture}(0,0)
%\put(-100,19){\makebox(0,0)[lb]{\footnotesize \@refnum}}
%\put(-100,12){\makebox(0,0)[lb]{\footnotesize \textit{issue}~: \@issue}}
%\put(-100,3){\makebox(0,0)[lb]{\footnotesize \textit{date}~: \@date}}
%\put(-100,-4){\makebox(0,0)[lb]{\footnotesize \textit{page}~: \thepage\ of
%\pageref{LastPage}}}
%\end{picture}}


\rhead{\begin{picture}(0,0)
\put(-100,27){\makebox(0,0)[lb]{\footnotesize \@refnum}}
\put(-100,18){\makebox(0,0)[lb]{\footnotesize \textit{issue}~: \@issue}}
\put(-100,8){\makebox(0,0)[lb]{\footnotesize \textit{date}~: \@date}}
\put(-100,0){\makebox(0,0)[lb]{\footnotesize \textit{page}~: \thepage\ of \pageref{LastPage}}}
\end{picture}}
% Andreas 12.07.2019

\lfoot{}
\cfoot{}
\rfoot{}

\message{note completed OK}
