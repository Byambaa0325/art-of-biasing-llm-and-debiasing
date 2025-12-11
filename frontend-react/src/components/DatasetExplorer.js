/**
 * Dataset Explorer Component
 *
 * Allows users to browse and select dataset entries for exploration
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  CircularProgress,
  Button,
  Tooltip,
  TextField,
} from '@mui/material';
import {
  Info,
  Refresh,
  Search,
} from '@mui/icons-material';
import axios from 'axios';

const DatasetExplorer = ({ onSelectEntry, apiBaseUrl }) => {
  const [entries, setEntries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [stats, setStats] = useState(null);

  // Filters
  const [stereotypeType, setStereotypeType] = useState('');
  const [biasType, setBiasType] = useState('');
  const [traitFilter, setTraitFilter] = useState('');

  useEffect(() => {
    fetchStats();
  }, []);

  useEffect(() => {
    fetchEntries();
  }, [page, rowsPerPage, stereotypeType, biasType, traitFilter]);

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${apiBaseUrl}/dataset/stats`);
      setStats(response.data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  };

  const fetchEntries = async () => {
    try {
      setLoading(true);
      const params = {
        limit: rowsPerPage,
        offset: page * rowsPerPage,
      };

      if (stereotypeType) params.stereotype_type = stereotypeType;
      if (traitFilter) params.trait = traitFilter;

      const response = await axios.get(`${apiBaseUrl}/dataset/entries`, { params });
      // Ensure each entry has an entry_index (use array index if not present)
      const entriesWithIndex = response.data.entries.map((entry, idx) => ({
        ...entry,
        entry_index: entry.entry_index !== undefined ? entry.entry_index : (page * rowsPerPage + idx),
      }));
      setEntries(entriesWithIndex);
      setTotal(response.data.total);
    } catch (err) {
      console.error('Failed to fetch entries:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (event, newPage) => {
    setPage(newPage);
  };

  const handleRowsPerPageChange = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleReset = () => {
    setStereotypeType('');
    setBiasType('');
    setTraitFilter('');
    setPage(0);
  };

  const getBiasTypeChips = (entry) => {
    const biasTypes = [
      'confirmation_bias',
      'anchoring_bias',
      'availability_bias',
      'framing_bias',
    ];

    return biasTypes.filter(bt => entry[`turn1_question_${bt}`]);
  };

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Dataset Explorer
        </Typography>
        <Tooltip title="Browse the EMGSD multi-turn dataset with pre-generated bias questions">
          <Info fontSize="small" color="action" />
        </Tooltip>
      </Box>

      {/* Stats Summary */}
      {stats && (
        <Box sx={{ mb: 2, p: 1.5, bgcolor: 'grey.100', borderRadius: 1 }}>
          <Typography variant="body2" fontWeight="bold" gutterBottom>
            Dataset Statistics
          </Typography>
          <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
            <Chip
              label={`Total: ${stats.total_entries.toLocaleString()}`}
              size="small"
              color="primary"
            />
            <Chip
              label={`Profession: ${(stats.stereotype_type_counts?.profession || 0).toLocaleString()}`}
              size="small"
            />
            <Chip
              label={`Nationality: ${(stats.stereotype_type_counts?.nationality || 0).toLocaleString()}`}
              size="small"
            />
            <Chip
              label={`Gender: ${(stats.stereotype_type_counts?.gender || 0).toLocaleString()}`}
              size="small"
            />
            <Chip
              label={`Religion: ${(stats.stereotype_type_counts?.religion || 0).toLocaleString()}`}
              size="small"
            />
          </Box>
        </Box>
      )}

      {/* Filters */}
      <Box sx={{ mb: 2, display: 'flex', gap: 2, flexWrap: 'wrap' }}>
        <FormControl sx={{ minWidth: 150, flexGrow: 1 }}>
          <InputLabel size="small">Stereotype Type</InputLabel>
          <Select
            value={stereotypeType}
            label="Stereotype Type"
            onChange={(e) => {
              setStereotypeType(e.target.value);
              setPage(0);
            }}
            size="small"
          >
            <MenuItem value="">All Types</MenuItem>
            <MenuItem value="profession">Profession</MenuItem>
            <MenuItem value="nationality">Nationality</MenuItem>
            <MenuItem value="gender">Gender</MenuItem>
            <MenuItem value="religion">Religion</MenuItem>
          </Select>
        </FormControl>

        <TextField
          label="Trait"
          value={traitFilter}
          onChange={(e) => {
            setTraitFilter(e.target.value);
            setPage(0);
          }}
          size="small"
          placeholder="e.g., bossy, lazy"
          sx={{ minWidth: 150, flexGrow: 1 }}
          InputProps={{
            startAdornment: <Search fontSize="small" sx={{ mr: 1, color: 'text.secondary' }} />,
          }}
        />

        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={handleReset}
          size="small"
        >
          Reset
        </Button>
      </Box>

      {/* Results Table */}
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Target Question</TableCell>
              <TableCell>Trait</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Bias Questions</TableCell>
              <TableCell>Action</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                  <CircularProgress size={24} />
                </TableCell>
              </TableRow>
            ) : entries.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary">
                    No entries found
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              entries.map((entry, index) => (
                <TableRow key={index} hover>
                  <TableCell>
                    <Typography variant="body2" fontWeight="medium">
                      {entry.target_question || entry.emgsd_text?.substring(0, 50) + '...'}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={entry.emgsd_trait}
                      size="small"
                      variant="outlined"
                      color="primary"
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="caption" color="text.secondary">
                      {entry.emgsd_stereotype_type}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Tooltip title="Number of bias types available for this entry">
                      <Chip
                        label={`${getBiasTypeChips(entry).length} bias types`}
                        size="small"
                        color="success"
                      />
                    </Tooltip>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="contained"
                      size="small"
                      onClick={() => onSelectEntry(entry)}
                    >
                      Explore
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      <TablePagination
        rowsPerPageOptions={[5, 10, 25, 50]}
        component="div"
        count={total}
        rowsPerPage={rowsPerPage}
        page={page}
        onPageChange={handlePageChange}
        onRowsPerPageChange={handleRowsPerPageChange}
      />
    </Paper>
  );
};

export default DatasetExplorer;
