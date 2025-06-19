import PyPDF2
from docx import Document
import re
import os
from typing import Dict, List, Any

class FileParser:
    def __init__(self):
        self.question_patterns = [
            r'^\d+\.\s*(.+?)(?=\n\d+\.|\n[A-D]\.|\n$)',  # 1. Question text
            r'^[A-Z]\.\s*(.+?)(?=\n[A-Z]\.|\n$)',  # A. Question text
            r'^Question\s*\d+:\s*(.+?)(?=\nQuestion|\n[A-D]\.|\n$)',  # Question 1: text
        ]
        
        self.answer_patterns = [
            r'^[A-D]\.\s*(.+?)(?=\n[A-D]\.|\n\d+\.|\n$)',  # A. Answer text
            r'^Answer:\s*(.+?)(?=\n\d+\.|\n$)',  # Answer: text
        ]
    
    def parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse PDF file and extract Q/A pairs"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return self._extract_qa_pairs(text)
                
        except Exception as e:
            return {
                'error': f'Failed to parse PDF: {str(e)}',
                'questions': [],
                'concepts': []
            }
    
    def parse_docx(self, file_path: str) -> Dict[str, Any]:
        """Parse DOCX file and extract Q/A pairs"""
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return self._extract_qa_pairs(text)
            
        except Exception as e:
            return {
                'error': f'Failed to parse DOCX: {str(e)}',
                'questions': [],
                'concepts': []
            }
    
    def _extract_qa_pairs(self, text: str) -> Dict[str, Any]:
        """Extract questions and answers from text"""
        lines = text.split('\n')
        questions = []
        concepts = []
        
        # Extract questions
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Check for question patterns
            for pattern in self.question_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    question_text = match.group(1).strip()
                    if len(question_text) > 10:  # Minimum question length
                        questions.append({
                            'question': question_text,
                            'line_number': i + 1,
                            'answers': self._find_answers(lines, i)
                        })
                    break
        
        # Extract concepts (key terms, definitions)
        concepts = self._extract_concepts(text)
        
        return {
            'questions': questions,
            'concepts': concepts,
            'total_questions': len(questions),
            'total_concepts': len(concepts)
        }
    
    def _find_answers(self, lines: List[str], question_line: int) -> List[str]:
        """Find answers following a question"""
        answers = []
        
        # Look for answers in the next few lines
        for i in range(question_line + 1, min(question_line + 10, len(lines))):
            line = lines[i].strip()
            if not line:
                continue
            
            # Check for answer patterns
            for pattern in self.answer_patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    answer_text = match.group(1).strip()
                    if len(answer_text) > 3:  # Minimum answer length
                        answers.append(answer_text)
                    break
            
            # Stop if we hit another question
            for pattern in self.question_patterns:
                if re.match(pattern, line, re.IGNORECASE):
                    return answers
        
        return answers
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract key concepts and definitions from text"""
        concepts = []
        
        # Look for definition patterns
        definition_patterns = [
            r'([A-Z][A-Za-z\s]+):\s*(.+?)(?=\n[A-Z]|\n\d+\.|\n$)',  # Term: Definition
            r'([A-Z][A-Za-z\s]+)\s*=\s*(.+?)(?=\n[A-Z]|\n\d+\.|\n$)',  # Term = Definition
            r'([A-Z][A-Za-z\s]+)\s*-\s*(.+?)(?=\n[A-Z]|\n\d+\.|\n$)',  # Term - Definition
        ]
        
        for pattern in definition_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                
                if len(term) > 2 and len(definition) > 10:
                    concepts.append({
                        'term': term,
                        'definition': definition
                    })
        
        return concepts
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate uploaded file"""
        if not os.path.exists(file_path):
            return {'valid': False, 'error': 'File does not exist'}
        
        file_size = os.path.getsize(file_path)
        if file_size > 20 * 1024 * 1024:  # 20MB limit
            return {'valid': False, 'error': 'File size exceeds 20MB limit'}
        
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in ['.pdf', '.docx']:
            return {'valid': False, 'error': 'Unsupported file type. Only PDF and DOCX files are allowed.'}
        
        return {'valid': True, 'file_size': file_size, 'file_type': file_extension} 