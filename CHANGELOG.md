# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-27

### Added
- Initial release of Digital Home Backend
- Zero-knowledge end-to-end encryption system
- User registration and authentication with JWT
- Family management (create, add members)
- Milestone tracking with encrypted content
- Docker support for easy deployment
- Version management with release.sh script
- Production-ready docker-compose configuration
- Nginx reverse proxy configuration
- Comprehensive API documentation

### Security
- All sensitive data encrypted on client-side
- RSA key pair generation for users
- AES encryption for family shared keys
- Password-based encryption for user private keys
- JWT-based authentication
- bcrypt password hashing

### Deployment
- Multi-stage Docker build for optimized images
- Docker Compose for local development
- Production Docker Compose configuration
- Health checks for all services
- Nginx configuration with rate limiting
- Support for SSL/TLS

### Documentation
- API documentation (API_DOCS.md)
- Deployment guide (DEPLOYMENT.md)
- README with quick start guide
- Encryption testing documentation

## [Unreleased]

### Planned
- [ ] User profile management
- [ ] File upload support
- [ ] Real-time notifications
- [ ] Admin dashboard
- [ ] Backup and restore tools
- [ ] Advanced monitoring and logging
