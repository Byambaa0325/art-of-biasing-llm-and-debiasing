import React from 'react';
import { Box, Typography, Accordion, AccordionSummary, AccordionDetails, Link, Chip } from '@mui/material';
import { ExpandMore, Article } from '@mui/icons-material';

const BIAS_SOURCES = {
  'Confirmation Bias': {
    definition: 'The tendency to interpret information in a way that confirms pre-existing beliefs.',
    sources: [
      { name: 'Sun & Kok (2025)', url: 'https://arxiv.org', description: 'Cognitive bias injection in prompts' },
      { name: 'BiasBuster (Echterhoff et al., 2024)', url: 'https://arxiv.org/pdf/2403.00811', description: 'Cognitive bias evaluation framework' },
    ],
    framework: 'BEATS Framework'
  },
  'Demographic Bias': {
    definition: 'Bias based on demographic characteristics such as race, gender, age, religion, etc.',
    sources: [
      { name: 'Neumann et al. (FAccT 2025)', url: 'https://arxiv.org', description: 'Representational vs. Allocative bias' },
      { name: 'BEATS Framework', url: 'https://arxiv.org', description: '29 comprehensive bias metrics' },
    ],
    framework: 'BEATS Framework'
  },
  'Anchoring Bias': {
    definition: 'The tendency to rely too heavily on the first piece of information encountered.',
    sources: [
      { name: 'Sun & Kok (2025)', url: 'https://arxiv.org', description: 'Cognitive bias taxonomy' },
      { name: 'BiasBuster (Echterhoff et al., 2024)', url: 'https://arxiv.org/pdf/2403.00811', description: 'Sequential bias evaluation' },
    ],
    framework: 'BiasBuster'
  },
  'Framing Bias': {
    definition: 'The way information is presented influences decision-making.',
    sources: [
      { name: 'Sun & Kok (2025)', url: 'https://arxiv.org', description: 'Cognitive bias patterns' },
      { name: 'BiasBuster (Echterhoff et al., 2024)', url: 'https://arxiv.org/pdf/2403.00811', description: 'Framing bias in decision-making' },
    ],
    framework: 'BiasBuster'
  },
  'Availability Bias': {
    definition: 'Over-reliance on easily recalled information rather than comprehensive evidence.',
    sources: [
      { name: 'Sun & Kok (2025)', url: 'https://arxiv.org', description: 'Availability bias patterns' },
    ],
    framework: 'BEATS Framework'
  },
  'Leading Question Bias': {
    definition: 'Questions phrased in a way that suggests a particular answer.',
    sources: [
      { name: 'Sun & Kok (2025)', url: 'https://arxiv.org', description: 'Leading question patterns' },
    ],
    framework: 'BEATS Framework'
  },
  'Stereotypical Assumption': {
    definition: 'Broad generalizations that may not apply to individuals.',
    sources: [
      { name: 'BEATS Framework', url: 'https://arxiv.org', description: 'Stereotype detection' },
    ],
    framework: 'BEATS Framework'
  },
};

function SourceDefinitions({ biasType }) {
  const sourceInfo = BIAS_SOURCES[biasType];
  
  if (!sourceInfo) {
    return (
      <Box sx={{ mt: 1 }}>
        <Typography variant="body2" color="text.secondary">
          Source information not available for this bias type.
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ mt: 1 }}>
      <Accordion>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Article fontSize="small" />
            <Typography variant="subtitle2">Definition & Sources</Typography>
            {sourceInfo.framework && (
              <Chip label={sourceInfo.framework} size="small" color="primary" />
            )}
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Box>
            <Typography variant="body2" sx={{ mb: 2, fontStyle: 'italic' }}>
              {sourceInfo.definition}
            </Typography>
            <Typography variant="subtitle2" gutterBottom>
              Research Sources:
            </Typography>
            {sourceInfo.sources.map((source, index) => (
              <Box key={index} sx={{ mb: 1 }}>
                <Link href={source.url} target="_blank" rel="noopener noreferrer">
                  {source.name}
                </Link>
                <Typography variant="caption" display="block" color="text.secondary">
                  {source.description}
                </Typography>
              </Box>
            ))}
          </Box>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
}

export default SourceDefinitions;

