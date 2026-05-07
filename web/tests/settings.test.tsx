import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SettingsPage from '../app/settings/page';
import * as api from '../lib/api';

vi.mock('../lib/api', () => ({
  getSources: vi.fn(),
  getKeywords: vi.fn(),
  createSource: vi.fn(),
  createKeyword: vi.fn(),
  deleteSource: vi.fn(),
  deleteKeyword: vi.fn(),
}));

describe('SettingsPage', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    vi.mocked(api.getSources).mockResolvedValue([
      {
        id: 1,
        name: 'Test Source',
        base_url: 'http://test.com',
        region: 'global',
        language: 'en',
        source_type: 'media',
        discovery_mode: 'search',
        priority: 1,
        active: true
      }
    ]);
    vi.mocked(api.getKeywords).mockResolvedValue([
      { id: 1, keyword: 'Test Keyword', active: true }
    ]);
  });

  afterEach(() => {
    cleanup();
  });

  it('renders settings page and loads data', async () => {
    render(<SettingsPage />);
    
    expect(screen.getByText('Settings / Configuration')).toBeDefined();
    
    await waitFor(() => {
      expect(screen.getByText('Test Source')).toBeDefined();
      expect(screen.getByText('Test Keyword')).toBeDefined();
    });
  });

  it('adds a new source', async () => {
    render(<SettingsPage />);
    
    const nameInput = screen.getByPlaceholderText('Name');
    const urlInput = screen.getByPlaceholderText('Base URL');
    const addButton = screen.getByText('Add Source');

    await userEvent.type(nameInput, 'New Source');
    await userEvent.type(urlInput, 'http://new.com');
    await userEvent.click(addButton);

    expect(api.createSource).toHaveBeenCalledWith({
      name: 'New Source',
      base_url: 'http://new.com',
      region: 'global',
      language: 'en',
      source_type: 'media',
      discovery_mode: 'search',
      priority: 1,
      active: true
    });
    
    await waitFor(() => {
      expect(api.getSources).toHaveBeenCalledTimes(2);
    });
  });

  it('adds a new keyword', async () => {
    render(<SettingsPage />);
    
    const keywordInput = screen.getByPlaceholderText('New keyword');
    const addButton = screen.getByText('Add');

    await userEvent.type(keywordInput, 'New Keyword');
    await userEvent.click(addButton);

    expect(api.createKeyword).toHaveBeenCalledWith({
      keyword: 'New Keyword',
      active: true
    });

    await waitFor(() => {
      expect(api.getKeywords).toHaveBeenCalledTimes(2);
    });
  });

  it('deletes a source', async () => {
    render(<SettingsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Source')).toBeDefined();
    });

    const deleteButtons = screen.getAllByText('Delete');
    // The first delete button is for the source
    await userEvent.click(deleteButtons[0]);

    expect(api.deleteSource).toHaveBeenCalledWith(1);
    
    await waitFor(() => {
      expect(api.getSources).toHaveBeenCalledTimes(2);
    });
  });

  it('deletes a keyword', async () => {
    render(<SettingsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Keyword')).toBeDefined();
    });

    const deleteButtons = screen.getAllByText('Delete');
    // The second delete button is for the keyword
    await userEvent.click(deleteButtons[1]);

    expect(api.deleteKeyword).toHaveBeenCalledWith(1);
    
    await waitFor(() => {
      expect(api.getKeywords).toHaveBeenCalledTimes(2);
    });
  });
});
