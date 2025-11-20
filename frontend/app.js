// Frontend JavaScript for Bias Analysis Tool

const API_BASE_URL = 'http://localhost:5000/api';

document.getElementById('analyzeBtn').addEventListener('click', analyzePrompt);

async function analyzePrompt() {
    const prompt = document.getElementById('promptInput').value.trim();
    
    if (!prompt) {
        alert('Please enter a prompt to analyze');
        return;
    }
    
    const resultsSection = document.getElementById('results');
    resultsSection.style.display = 'block';
    resultsSection.innerHTML = '<div class="loading">Analyzing prompt...</div>';
    
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt: prompt })
        });
        
        if (!response.ok) {
            throw new Error('Analysis failed');
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        resultsSection.innerHTML = `
            <div class="error">
                <strong>Error:</strong> Could not analyze prompt. Make sure the backend server is running on port 5000.
            </div>
        `;
    }
}

function displayResults(data) {
    const resultsSection = document.getElementById('results');
    
    let html = '';
    
    // Bias Detection Section
    html += `
        <section id="biasDetection" class="result-card">
            <h2>🔍 Detected Biases</h2>
            ${displayBiasScore(data.detected_biases)}
            ${displayBiasDetails(data.detected_biases)}
        </section>
    `;
    
    // Bias Injection Section
    html += `
        <section id="biasInjection" class="result-card">
            <h2>⚠️ How This Prompt Can Be Biased</h2>
            <p class="section-explanation">See how subtle changes can introduce different types of bias:</p>
            ${displayBiasedVersions(data.biased_versions)}
        </section>
    `;
    
    // Debiasing Section
    html += `
        <section id="debiasing" class="result-card">
            <h2>✨ How to Normalize/Debias This Prompt</h2>
            <p class="section-explanation">Learn methods to remove bias and make your prompt more fair:</p>
            ${displayDebiasedVersions(data.debiased_versions)}
        </section>
    `;
    
    resultsSection.innerHTML = html;
}

function displayBiasScore(biases) {
    const score = biases.overall_bias_score;
    const percentage = Math.round(score * 100);
    let color = '#51cf66'; // green
    let label = 'Low Bias';
    
    if (score > 0.6) {
        color = '#ff6b6b'; // red
        label = 'High Bias';
    } else if (score > 0.3) {
        color = '#ffd43b'; // yellow
        label = 'Moderate Bias';
    }
    
    return `
        <div class="bias-score">
            <div class="bias-score-value" style="color: ${color}">${percentage}%</div>
            <div class="bias-score-label">${label}</div>
        </div>
    `;
}

function displayBiasDetails(biases) {
    let html = '';
    
    // Framework alignments
    if (biases.framework_alignments && biases.framework_alignments.length > 0) {
        html += `<div class="bias-item" style="border-left-color: #339af0;">
            <h3>📚 Research Framework Alignments</h3>
            <p><strong>Based on:</strong> ${biases.framework_alignments.join(', ')}</p>
        </div>`;
    }
    
    // Bias classification summary
    if (biases.bias_classification) {
        const classifications = [];
        if (biases.bias_classification.representational) classifications.push('Representational');
        if (biases.bias_classification.allocative) classifications.push('Allocative');
        if (biases.bias_classification.cognitive) classifications.push('Cognitive');
        if (biases.bias_classification.structural) classifications.push('Structural');
        
        if (classifications.length > 0) {
            html += `<div class="bias-item" style="border-left-color: #339af0;">
                <h3>🏷️ Bias Classifications</h3>
                <p><strong>Types detected:</strong> ${classifications.join(', ')}</p>
                ${biases.bias_classification.representational ? 
                    '<p style="margin-top: 8px;"><em>Representational:</em> Affects how groups are portrayed</p>' : ''}
                ${biases.bias_classification.allocative ? 
                    '<p><em>Allocative:</em> Affects resource/outcome distribution (Neumann et al., FAccT 2025)</p>' : ''}
            </div>`;
        }
    }
    
    // Representational biases
    if (biases.representational_biases && biases.representational_biases.length > 0) {
        html += '<div class="bias-item"><h3>🎭 Representational Biases</h3>';
        html += '<p style="color: #666; font-size: 0.9em; margin-bottom: 10px;">How groups are portrayed or represented</p>';
        biases.representational_biases.forEach(bias => {
            html += `<p><strong>${bias.category}:</strong> ${bias.explanation}</p>`;
        });
        html += '</div>';
    }
    
    // Allocative biases
    if (biases.allocative_biases && biases.allocative_biases.length > 0) {
        html += '<div class="bias-item"><h3>⚖️ Allocative Biases</h3>';
        html += '<p style="color: #666; font-size: 0.9em; margin-bottom: 10px;">How resources/outcomes are distributed</p>';
        biases.allocative_biases.forEach(bias => {
            html += `<p><strong>${bias.category}:</strong> ${bias.explanation}</p>`;
        });
        html += '</div>';
    }
    
    // Demographic biases (general)
    if (biases.demographic_biases && biases.demographic_biases.length > 0) {
        html += '<div class="bias-item"><h3>👥 Demographic Biases</h3>';
        biases.demographic_biases.forEach(bias => {
            const biasTypes = bias.bias_type ? ` (${bias.bias_type.join(', ')})` : '';
            html += `<p><strong>${bias.category}${biasTypes}:</strong> ${bias.explanation}</p>`;
        });
        html += '</div>';
    }
    
    // Cognitive biases
    if (biases.cognitive_biases && biases.cognitive_biases.length > 0) {
        html += '<div class="bias-item"><h3>🧠 Cognitive Biases</h3>';
        html += '<p style="color: #666; font-size: 0.9em; margin-bottom: 10px;">Based on BEATS Framework & Sun & Kok (2025)</p>';
        biases.cognitive_biases.forEach(bias => {
            const framework = bias.framework ? ` <span style="color: #999; font-size: 0.85em;">[${bias.framework}]</span>` : '';
            html += `<p><strong>${bias.type.replace(/_/g, ' ').toUpperCase()}${framework}:</strong> ${bias.explanation}</p>`;
        });
        html += '</div>';
    }
    
    // Structural biases
    if (biases.structural_biases && biases.structural_biases.length > 0) {
        html += '<div class="bias-item"><h3>🏗️ Structural Biases</h3>';
        html += '<p style="color: #666; font-size: 0.9em; margin-bottom: 10px;">Based on Xu et al. (LREC 2024)</p>';
        biases.structural_biases.forEach(bias => {
            html += `<p><strong>${bias.type.replace(/_/g, ' ').toUpperCase()}:</strong> ${bias.explanation}</p>`;
        });
        html += '</div>';
    }
    
    // Leading questions
    if (biases.leading_questions && biases.leading_questions.length > 0) {
        html += '<div class="bias-item"><h3>❓ Leading Questions</h3>';
        biases.leading_questions.forEach(bias => {
            html += `<p>${bias.explanation}</p>`;
        });
        html += '</div>';
    }
    
    // Assumption-laden language
    if (biases.assumption_laden && biases.assumption_laden.length > 0) {
        html += '<div class="bias-item"><h3>📋 Assumption-Laden Language</h3>';
        biases.assumption_laden.forEach(bias => {
            html += `<p>${bias.explanation}</p>`;
        });
        html += '</div>';
    }
    
    if (html === '') {
        html = '<p style="color: #51cf66;">✅ No obvious biases detected in this prompt!</p>';
    }
    
    return html;
}

function displayBiasedVersions(biasedVersions) {
    if (biasedVersions.length === 0) {
        return '<p style="color: #51cf66;">✅ This prompt is already neutral - no bias injection examples available.</p>';
    }
    
    let html = '';
    biasedVersions.forEach(version => {
        html += `
            <div class="biased-version">
                <h3>
                    <span class="bias-badge">${version.bias_added}</span>
                </h3>
                <div class="prompt-text">${escapeHtml(version.biased_prompt)}</div>
                <div class="explanation">
                    <strong>What changed:</strong> ${version.explanation}
                </div>
                <div class="how-it-works">
                    <strong>How it works:</strong> ${version.how_it_works}
                </div>
            </div>
        `;
    });
    
    return html;
}

function displayDebiasedVersions(debiasedVersions) {
    if (debiasedVersions.length === 0) {
        return '<p>No debiasing methods available for this prompt.</p>';
    }
    
    let html = '';
    debiasedVersions.forEach(version => {
        html += `
            <div class="debiased-version">
                <h3>
                    <span class="method-badge">${version.method}</span>
                </h3>
                <div class="prompt-text">${escapeHtml(version.debiased_prompt)}</div>
                <div class="explanation">
                    <strong>What this does:</strong> ${version.explanation}
                </div>
                <div class="how-it-works">
                    <strong>How it works:</strong> ${version.how_it_works}
                </div>
                ${version.steps ? `
                    <div class="how-it-works">
                        <strong>Steps taken:</strong>
                        <ul class="steps-list">
                            ${version.steps.map(step => `<li>${step}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
            </div>
        `;
    });
    
    return html;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

