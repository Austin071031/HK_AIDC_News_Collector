import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { 
  getSources, createSource, deleteSource, 
  getKeywords, createKeyword, deleteKeyword 
} from '../lib/api';

describe('Config Editor API Wrappers', () => {
  const originalFetch = global.fetch;

  beforeEach(() => {
    global.fetch = vi.fn();
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  describe('getSources', () => {
    it('fetches sources from /api/sources', async () => {
      const mockSources = [{ id: 1, name: 'Test Source' }];
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockSources
      });

      const result = await getSources();
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sources',
        { cache: 'no-store' }
      );
      expect(result).toEqual(mockSources);
    });

    it('throws error when fetch fails', async () => {
      (global.fetch as any).mockResolvedValue({
        ok: false
      });
      await expect(getSources()).rejects.toThrow('Failed to fetch sources');
    });
  });

  describe('createSource', () => {
    it('posts to /api/sources with payload', async () => {
      const payload = {
        name: 'New Source',
        base_url: 'http://test.com',
        region: 'global',
        language: 'en',
        source_type: 'media',
        discovery_mode: 'search',
        priority: 1,
        active: true
      };
      const mockResponse = { id: 2, ...payload };
      
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse
      });

      const result = await createSource(payload);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sources',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('throws error when creation fails', async () => {
      (global.fetch as any).mockResolvedValue({ ok: false });
      await expect(createSource({ name: 'Test' } as any)).rejects.toThrow('Failed to create source');
    });
  });

  describe('deleteSource', () => {
    it('sends DELETE to /api/sources/:id', async () => {
      (global.fetch as any).mockResolvedValue({ ok: true });
      await deleteSource(1);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/sources/1',
        { method: 'DELETE' }
      );
    });

    it('throws error when deletion fails', async () => {
      (global.fetch as any).mockResolvedValue({ ok: false });
      await expect(deleteSource(1)).rejects.toThrow('Failed to delete source');
    });
  });

  describe('getKeywords', () => {
    it('fetches keywords from /api/keywords', async () => {
      const mockKeywords = [{ id: 1, keyword: 'AI', active: true }];
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockKeywords
      });

      const result = await getKeywords();
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/keywords',
        { cache: 'no-store' }
      );
      expect(result).toEqual(mockKeywords);
    });

    it('throws error when fetch fails', async () => {
      (global.fetch as any).mockResolvedValue({ ok: false });
      await expect(getKeywords()).rejects.toThrow('Failed to fetch keywords');
    });
  });

  describe('createKeyword', () => {
    it('posts to /api/keywords with payload', async () => {
      const payload = { keyword: 'ML', active: true };
      const mockResponse = { id: 2, ...payload };
      
      (global.fetch as any).mockResolvedValue({
        ok: true,
        json: async () => mockResponse
      });

      const result = await createKeyword(payload);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/keywords',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('throws error when creation fails', async () => {
      (global.fetch as any).mockResolvedValue({ ok: false });
      await expect(createKeyword({ keyword: 'Test' } as any)).rejects.toThrow('Failed to create keyword');
    });
  });

  describe('deleteKeyword', () => {
    it('sends DELETE to /api/keywords/:id', async () => {
      (global.fetch as any).mockResolvedValue({ ok: true });
      await deleteKeyword(1);
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/keywords/1',
        { method: 'DELETE' }
      );
    });

    it('throws error when deletion fails', async () => {
      (global.fetch as any).mockResolvedValue({ ok: false });
      await expect(deleteKeyword(1)).rejects.toThrow('Failed to delete keyword');
    });
  });
});
