<<<<<<< HEAD
# cyber-backend-api
=======
# Cyber Intelligence Backend API

A FastAPI-based backend service for cyber intelligence queries, designed for seamless integration with Bolt.new.

## 🚀 Features

- **FastAPI Backend**: High-performance async API server
- **Supabase Integration**: Direct connection to cyber intelligence database
- **Comprehensive Search**: Search across 38,000+ records
- **Multiple Endpoints**: Vulnerabilities, threats, expert knowledge
- **Bolt.new Ready**: Optimized for direct import and deployment

## 📊 Database

- **38,226+ Records** across multiple tables
- **Expert Knowledge**: 17,445 articles and guides
- **Vulnerabilities**: 120 CVE entries
- **Threat Indicators**: 17,151 security indicators
- **Malware Signatures**: 2,000 patterns
- **Network Security Data**: 1,500 configurations

## 🛠️ Quick Start

### For Bolt.new Import

1. **Import this repository** into Bolt.new
2. **Configure environment variables**:
   ```env
   SUPABASE_URL=https://odczfcygmifymbfqpmra.supabase.co
   SUPABASE_KEY=your_service_role_key_here
   PORT=8000
   ```
3. **Deploy** - Bolt.new will handle the rest!

### Local Development

```bash
# Clone the repository
git clone https://github.com/yourusername/cyber-backend-api.git
cd cyber-backend-api

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your Supabase credentials

# Run the server
python main.py
```

## 📡 API Endpoints

### Core Endpoints
- `GET /` - API information and status
- `GET /stats` - Database statistics
- `GET /search?query={query}` - Search all data
- `GET /vulnerabilities` - CVE database
- `GET /threats` - Threat indicators
- `GET /expert-knowledge` - Articles and guides

### Example Queries
```bash
# Search for CISO information
GET /search?query=ciso&limit=5

# Get vulnerability data
GET /vulnerabilities?severity=high

# Get threat indicators
GET /threats?indicator_type=domain
```

## 🔧 Configuration

### Environment Variables
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_service_role_key
PORT=8000
```

### Dependencies
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `supabase` - Database client
- `python-dotenv` - Environment management

## 🚀 Deployment

### Bolt.new (Recommended)
1. Import this GitHub repository
2. Bolt.new will automatically:
   - Install dependencies
   - Configure the server
   - Deploy the API
   - Provide access URLs

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --host 0.0.0.0 --port 8000
```

## � Data Sources

This backend connects to a Supabase database containing:
- Web-scraped cybersecurity articles
- Vulnerability databases (CVEs)
- Threat intelligence feeds
- Malware signature databases
- Network security configurations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - feel free to use this for your cyber intelligence projects!

## 🔗 Links

- **API Documentation**: Available at `/docs` when running locally
- **Supabase Dashboard**: https://supabase.com/dashboard
- **Bolt.new**: https://bolt.new

---

**Built for Bolt.new** - Seamless AI-powered deployment! ⚡
>>>>>>> master
